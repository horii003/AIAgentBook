# orchestrator_agent.py 解説

## このファイルの役割

`OrchestratorAgent` は**申請受付の窓口**です。社員が何かを申請したいとき、まずこのエージェントが対話を受け取り、「交通費精算なのか、それとも一般経費精算なのか」を判断して、適切な専門エージェントに処理を引き渡します。

```
社員
 │
 │ 入力
 ▼
OrchestratorAgent（このファイル）
 ├─ 交通費の申請 → transportation_expense_agent へ
 └─ 経費の申請   → general_expense_agent へ
```

---

## 1. Strandsライブラリ / Agent の使い方

### 1-1. Agent() のコンストラクタ

`Agent()` はStrandsライブラリが提供するクラスで、LLM（大規模言語モデル）を使った対話エージェントを組み立てます。`_initialize_agent()` で各引数を設定しています。

```python
# agents/orchestrator_agent.py  47〜79行
def _initialize_agent(self) -> Agent:
    cfg = settings.orchestrator
    loop_control_hook = LoopControlHook(     #(G) ループ制御
        max_iterations=cfg.max_iterations,
        agent_name="申請受付窓口エージェント",
    )

    return Agent(
        model=ModelConfig.get_model(),          # (A) 使用するLLMモデル
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,  # (B) エージェントへの基本指示
        tools=[transportation_expense_agent, general_expense_agent],  # (C) 使えるツール
        agent_id="orchestrator_agent",
        name="申請受付窓口エージェント",
        description="...",
        conversation_manager=SlidingWindowConversationManager(  # (D) 会話履歴の管理
            window_size=cfg.window_size,
            should_truncate_results=True,
            per_turn=False,
        ),
        callback_handler=None,
        retry_strategy=ModelRetryStrategy(      # (E) エラー時のリトライ設定
            max_attempts=cfg.max_attempts,
            initial_delay=cfg.initial_delay,
            max_delay=cfg.max_delay,
        ),
        hooks=[loop_control_hook],              # (F) ループ制御フック
        session_manager=self._session_manager,
    )
```

各引数の意味を順に見ていきます。

---

#### (A) model — 使用するLLMモデル

```python
model=ModelConfig.get_model()
```

どのAIモデル（例：Claude Sonnet）を使うかを指定します。`ModelConfig.get_model()` は設定ファイルからモデル名を読み込むヘルパーです。ここを変えるだけでモデルを切り替えられます。

---

#### (B) system_prompt — エージェントへの基本指示

```python
system_prompt=ORCHESTRATOR_SYSTEM_PROMPT
```

LLMに対して「あなたはどういう役割で、どう振る舞うべきか」を伝えるテキストです。人間で言えば**仕事の引き継ぎ書**に相当します。`ORCHESTRATOR_SYSTEM_PROMPT` は別ファイル（`prompt/prompt_orchestrator.py`）に定義されており、「申請種別を判断して適切なエージェントに渡せ」といった指示が書かれています。

---

#### (C) tools — エージェントが使えるツール

```python
tools=[transportation_expense_agent, general_expense_agent]
```

これが**Agent as Tools パターン**の核心です。

通常 `tools` にはPythonの関数（APIを呼ぶ、計算するなど）を渡しますが、このコードでは**別のエージェント**を渡しています。オーケストレーターはLLMの判断で「交通費の話だ」と判断したら `transportation_expense_agent` を、「経費の話だ」と判断したら `general_expense_agent` を自動的に呼び出します。

```
# ツールとして登録されている関数の定義（別ファイル）
@tool(context=True)
def transportation_expense_agent(query: str, tool_context: ToolContext) -> str:
    ...
```

`@tool` デコレータが付いた関数は、StrandsがLLMに「これが使えるツールだ」と認識させます。LLMはツールの名前・引数・docstringを読んで、いつ呼ぶべきかを判断します。

---

#### (D) SlidingWindowConversationManager — 会話履歴の管理

```python
conversation_manager=SlidingWindowConversationManager(
    window_size=cfg.window_size,
    should_truncate_results=True,
    per_turn=False,
)
```

LLMには**コンテキストウィンドウ**（一度に処理できるトークン数）の上限があります。会話が長くなるとすべての履歴を送れなくなるため、`SlidingWindowConversationManager` は直近 `window_size` ターン分だけを保持し、古い内容を自動的に捨てます。

```
会話 1 ターン目: [メッセージ1]
会話 2 ターン目: [メッセージ1, メッセージ2]
会話 3 ターン目: [メッセージ1, メッセージ2, メッセージ3]
      ↓ window_size=2 の場合
会話 4 ターン目: [メッセージ3, メッセージ4]  ← メッセージ1,2は捨てる
```

---

#### (E) ModelRetryStrategy — エラー時のリトライ設定

```python
retry_strategy=ModelRetryStrategy(
    max_attempts=cfg.max_attempts,   # 最大試行回数
    initial_delay=cfg.initial_delay, # 最初のリトライまでの待機秒数
    max_delay=cfg.max_delay,         # 待機時間の上限秒数
)
```

APIはネットワーク障害や一時的な過負荷でエラーを返すことがあります。`ModelRetryStrategy` は失敗したとき自動で再試行します。`initial_delay` から始まり、失敗のたびに待機時間を延ばしながら `max_delay` を超えないよう制御します（指数バックオフ）。

---

#### (F) hooks — ループ制御フック

```python
hooks=[loop_control_hook]
```

エージェントが無限ループに陥ることを防ぐ仕組みです。`LoopControlHook` はエージェントの実行回数を数え、`max_iterations` を超えたら `LoopLimitError` を発生させて強制停止します。

---

### 1-2. エージェントの呼び出し

組み立てた `Agent` インスタンスは、**関数のように呼び出す**だけで動作します（`__call__` が実装されています）。

```python
# agents/orchestrator_agent.py  154〜158行
response = self._agent(
    user_input,                                 # ユーザーの入力テキスト
    invocation_state=invocation_state.model_dump(),  # 付加情報（後述）
)
return str(response)
```

`self._agent(user_input)` を呼ぶと、Strandsが内部で以下を実行します。

```
1. system_prompt + 会話履歴 + user_input をLLMに送る
2. LLMがツール呼び出しを指示してきたら該当ツールを実行する
3. ツール結果をLLMに返す（必要なら繰り返す）
4. LLMが最終的な文章を返したらそれが response になる
```

---

## 2. 対話ループ

### 2-1. メインループの構造

`run()` が対話の入り口です。`while True` で無限ループを作り、ユーザーが `exit` を入力したときだけ `break` して終了します。

```python
# agents/orchestrator_agent.py  81〜110行
def run(self) -> None:
    print("============================================================")
    print("こちらは申請受付窓口エージェントです")
    # ...（案内メッセージ）
    print("============================================================")

    while True:                                       # (1) 無限ループ開始
        try:
            user_input = input("\n\n入力内容（終了時はquit）: ").strip()
            if not user_input:                        # (2) 空入力は無視
                continue

            if not self._handle_user_input(user_input):  # (3) 入力を処理
                break                                 # (4) Falseが返ったら終了

        except KeyboardInterrupt:                     # (5) Ctrl+C を捕捉
            print("\n\n" + ErrorHandler.handle_keyboard_interrupt(KeyboardInterrupt()))
            break

    _logger.info("対話ループ終了: session_id=%s", self._session_id)
```

ポイントを整理します。

| 番号 | コード | 意味 |
|------|--------|------|
| (1) | `while True:` | 明示的に終了するまで繰り返す |
| (2) | `if not user_input: continue` | 何も入力せずEnterを押した場合はスキップ |
| (3) | `self._handle_user_input(user_input)` | 入力の処理を別メソッドに委譲 |
| (4) | `break` | `False` が返ったら（終了コマンド）ループを抜ける |
| (5) | `except KeyboardInterrupt:` | ターミナルで Ctrl+C が押されたときも安全に終了 |

---

### 2-2. 入力の振り分け

`_handle_user_input()` はユーザーの入力を3種類に分類します。

```python
# agents/orchestrator_agent.py  112〜136行
def _handle_user_input(self, user_input: str) -> bool:
    # ① 終了コマンド
    if user_input.lower() in ("exit", "quit", "終了"):
        print("\nセッションを終了します。お疲れ様でした。")
        return False          # ← Falseを返すと呼び出し元でbreakされる

    # ② リセットコマンド
    if user_input.lower() in ("reset", "リセット", "最初から"):
        self._reset_session()
        print("\nセッションをリセットしました。最初からやり直します。")
        return True           # ← Trueを返すとループが継続される

    # ③ 通常の申請入力
    response = self._execute_agent(user_input)
    print(f"\nシステム> {response}")
    return True
```

`user_input.lower()` で小文字に統一しているのは、`"Exit"` や `"EXIT"` のような表記ゆれに対応するためです。

戻り値 `bool` の意味：
- `True` → 対話を続ける
- `False` → 対話を終了する（`run()` の `while True` を `break` させる）

---

### 2-3. エージェント実行と例外処理

`_execute_agent()` は実際にLLMを呼び出す部分です。ここで発生しうるエラーを種類ごとに捕捉しています。

```python
# agents/orchestrator_agent.py  138〜184行
def _execute_agent(self, user_input: str) -> str:
    invocation_state = InvocationState(
        applicant_name=self._applicant_name,
        application_date=datetime.now().strftime("%Y-%m-%d"),
        session_id=self._session_id,
    )

    try:
        response = self._agent(
            user_input,
            invocation_state=invocation_state.model_dump(),
        )
        return str(response)

    except KeyboardInterrupt as e:
        # Ctrl+C: ユーザーが中断した
        return ErrorHandler.handle_keyboard_interrupt(e)

    except LoopLimitError as e:
        # エージェントが無限ループに近い状態になった
        return ErrorHandler.handle_loop_limit_error(e)

    except RuntimeError as e:
        # Strandsや実行環境のエラー
        return ErrorHandler.handle_runtime_error(e)

    except Exception as e:
        # それ以外の予期しないエラー
        return ErrorHandler.handle_unexpected_error(e)
```

**なぜ例外ごとに分けるのか？**

例外を一つの `except Exception` だけで受けると、どんなエラーが起きたか区別できません。種類ごとに分けることで、ユーザーへのメッセージや後処理を変えられます。例えば `LoopLimitError` は「少し待ってから再試行してください」と案内できますが、`RuntimeError` は「システム管理者に連絡してください」という案内が適切です。

---

## 3. 状態管理

### 3-1. InvocationState — エージェント間で情報を共有する

エージェントが別のエージェント（ツール）を呼び出すとき、「この申請者は誰か」「申請日はいつか」といった情報を渡す必要があります。それを担うのが `InvocationState` です。

```python
# agents/orchestrator_agent.py  147〜157行
invocation_state = InvocationState(
    applicant_name=self._applicant_name,   # 申請者名
    application_date=datetime.now().strftime("%Y-%m-%d"),  # 今日の日付
    session_id=self._session_id,           # セッションID
)

response = self._agent(
    user_input,
    invocation_state=invocation_state.model_dump(),  # dictに変換して渡す
)
```

`model_dump()` はPydanticモデルを辞書（`dict`）に変換するメソッドです。Strandsはこの辞書を `ToolContext.invocation_state` として各ツールに自動で渡します。

```
OrchestratorAgent
 └─ self._agent(user_input, invocation_state={...})
       └─ transportation_expense_agent（ツール呼び出し）
             └─ calculate_transportation_cost（ツール呼び出し）
                   └─ tool_context.invocation_state.get("application_date")  ← ここで参照できる
```

申請日を `calculate_transportation_cost` に渡すことで、移動日が申請期限を過ぎているかのチェックが可能になっています。

---

### 3-2. セッション管理とリセット

**セッション**とは「ひとつの申請作業の流れ」です。セッションIDで会話履歴や処理状態を区別します。

```python
# agents/orchestrator_agent.py  32〜45行（__init__）
def __init__(self, applicant_name: str) -> None:
    self._applicant_name = applicant_name
    self._session_id = SessionManagerFactory.generate_session_id()  # 一意なIDを生成
    self._session_manager = SessionManagerFactory.create(self._session_id)
    self._agent = self._initialize_agent()
```

ユーザーが `reset` と入力したとき、`_reset_session()` が呼ばれます。

```python
# agents/orchestrator_agent.py  186〜194行
def _reset_session(self) -> None:
    old_session_id = self._session_id
    self._session_id = SessionManagerFactory.generate_session_id()   # 新しいIDを生成
    self._session_manager = SessionManagerFactory.create(self._session_id)
    self._agent = self._initialize_agent()                           # Agentを再生成
    _logger.info(
        "セッションリセット: old=%s, new=%s", old_session_id, self._session_id,
    )
```

**なぜAgentを再生成するのか？**

`Agent` インスタンスは内部に会話履歴（`SlidingWindowConversationManager`）を持っています。リセット時に同じインスタンスを使い続けると、過去の会話が残ってしまいます。新しいインスタンスを作り直すことで、確実に**まっさらな状態**から始められます。

---

## まとめ：3つの仕組みの関係

```
run()（対話ループ）
  │
  │  ユーザー入力
  ▼
_handle_user_input()
  │
  │  通常入力
  ▼
_execute_agent()
  │
  │  InvocationState（申請者名・日付・セッションID）を付加
  ▼
self._agent()（Strandsが管理するLLM呼び出し）
  │
  ├─ LLMが交通費と判断 → transportation_expense_agent（ツール）を呼び出す
  └─ LLMが経費と判断   → general_expense_agent（ツール）を呼び出す
```

| 仕組み | 役割 | 主なコード |
|--------|------|------------|
| Agent の組み立て | LLMモデル・ツール・リトライ設定をまとめる | `_initialize_agent()` |
| 対話ループ | ユーザー入力を受け取り応答を返し続ける | `run()`, `_handle_user_input()` |
| 状態管理 | 申請者情報をエージェント間で引き継ぐ | `InvocationState`, `_reset_session()` |
