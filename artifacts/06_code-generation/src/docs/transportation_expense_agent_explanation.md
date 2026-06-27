# transportation_expense_agent.py 解説

## このファイルの役割

交通費精算に特化した**専門エージェント**です。オーケストレーターから「交通費の申請だ」と判断されたとき、このファイルの関数が呼び出されます。ユーザーと対話しながら移動情報を収集し、運賃計算・期限チェック・申請書生成までを行います。

このファイルは **2つの層**で構成されています。

```
オーケストレーター
  │
  │  ツールとして呼び出す
  ▼
transportation_expense_agent()   ← ① 公開関数（@tool デコレータ付き）
  │
  │  エージェントを組み立てて実行する
  ▼
_build_transportation_expense_agent()  ← ② プライベート関数（Agent を生成）
```

---

## 1. @tool デコレータ

### 1-1. デコレータとは

デコレータとは、関数の定義の直前に `@名前` と書くことで、その関数に**追加の機能を付与する仕組み**です。

```python
# agents/transportation_expense_agent.py  57〜58行
@tool(context=True)
def transportation_expense_agent(query: str, tool_context: ToolContext) -> str:
```

`@tool` はStrandsが提供するデコレータで、「この関数はエージェントのツールとして使える」とStrandsに登録します。デコレータを付けるだけでよく、呼び出し側のコードを変更する必要はありません。

---

### 1-2. context=True と ToolContext

```python
@tool(context=True)
def transportation_expense_agent(query: str, tool_context: ToolContext) -> str:
```

`context=True` を指定すると、Strandsが `tool_context` 引数を**自動で渡してくれます**。LLMがこのツールを呼び出すとき、`query` だけを指定すれば `tool_context` はStrandsが自動で注入します。

`ToolContext` の中に何が入っているかというと：

```python
# base_agent.py  127〜129行（invoke_specialist_agent 内）
state = tool_context.invocation_state
applicant_name = state.get("applicant_name", "")     # 申請者名
application_date = state.get("application_date", "")  # 申請日
session_id = state.get("session_id", "")              # セッションID
```

オーケストレーターが `invocation_state` に詰めた情報がここで参照できます。ToolContext はStrandsがエージェント間の情報の橋渡し役として機能します。

```
orchestrator_agent.py
  └─ self._agent(user_input, invocation_state={"applicant_name": ..., ...})
                                     │
                                     │ Strandsが自動で伝達
                                     ▼
transportation_expense_agent.py
  └─ tool_context.invocation_state  ← ここで受け取れる
```

---

### 1-3. docstring がツールの説明になる

```python
@tool(context=True)
def transportation_expense_agent(query: str, tool_context: ToolContext) -> str:
    """交通費精算申請を処理する専門エージェント。

    ユーザーとの対話を通じて交通費精算に必要な情報を収集し、
    運賃計算・申請期限チェック・申請書生成を行う。

    Args:
        query: オーケストレーターからの質問・指示テキスト
    ...
    """
```

LLMはツールを呼び出す際、**関数名・引数名・docstring を読んで「いつ使うべきか」を判断します**。このdocstringが「交通費精算に関する処理だ」と書いてあるから、オーケストレーターのLLMは交通費に関する入力が来たときにこのツールを選択します。

---

## 2. Agent as Tools パターンの受け手側

### 2-1. 全体の流れ

このファイルは Agent as Tools パターンの「**ツールとして呼ばれる側**」です。オーケストレーターから見ると単なるツール関数ですが、中身は**別のエージェント（LLM）**を動かしています。

```
オーケストレーター（LLM）
  │  「交通費の話だ。transportation_expense_agent を呼ぼう」
  │
  └─ transportation_expense_agent(query="出張の交通費を申請したい")
        │
        │  invocation_state から申請者情報・申請日を取り出す
        │  deadline（申請期限）を計算する
        │
        └─ _build_transportation_expense_agent() で Agent を組み立てる
              │
              └─ agent(query)  ← 交通費専門のLLMが動く
                    │
                    ├─ calculate_transportation_cost（ツール）を呼ぶ
                    └─ generate_transportation_expense_form（ツール）を呼ぶ
```

---

### 2-2. 公開関数：transportation_expense_agent()

```python
# agents/transportation_expense_agent.py  57〜76行
@tool(context=True)
def transportation_expense_agent(query: str, tool_context: ToolContext) -> str:
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-002",
        deadline_months=settings.transportation_expense.deadline_months,
        build_agent=_build_transportation_expense_agent,
    )
```

この関数自体はとてもシンプルで、処理のほとんどを `invoke_specialist_agent()` に委譲しています。`build_agent=_build_transportation_expense_agent` と渡しているのがポイントで、「エージェントを組み立てる方法」を引数として渡しています（コールバック関数）。

---

### 2-3. invoke_specialist_agent() が行う共通処理

`invoke_specialist_agent()` は `base_agent.py` に定義された共通ヘルパーです。交通費・一般経費など複数の専門エージェントで同じ処理をまとめています。

```python
# base_agent.py  105〜153行
def invoke_specialist_agent(
    query, tool_context, agent_id, deadline_months, build_agent
) -> str:
    # ① invocation_state から情報を取り出す
    state = tool_context.invocation_state
    applicant_name = state.get("applicant_name", "")
    application_date = state.get("application_date", "")
    session_id = state.get("session_id", "")

    # ② 申請期限を計算する
    deadline = calculate_deadline(application_date, deadline_months)

    # ③ エージェントを組み立てる（build_agent は _build_transportation_expense_agent）
    agent = build_agent(session_id, applicant_name, application_date, deadline)

    # ④ session_id を除外して子エージェントに渡す情報を絞る
    child_invocation_state = {
        "applicant_name": applicant_name,
        "application_date": application_date,
    }

    # ⑤ エージェントを実行する
    try:
        response = agent(query, invocation_state=child_invocation_state)
        return str(response)
    except LoopLimitError as e:
        return ErrorHandler.handle_loop_limit_error(e)
    except Exception as e:
        return ErrorHandler.handle_unexpected_error(e)
```

④で `session_id` を除外しているのは、セッション管理はオーケストレーターが担うためです。子エージェントには「この申請者・この日付」という最低限の情報だけを渡します。

---

### 2-4. プライベート関数：_build_transportation_expense_agent()

```python
# agents/transportation_expense_agent.py  20〜54行
def _build_transportation_expense_agent(
    session_id: str,
    applicant_name: str,
    application_date: str,
    deadline: str,
) -> Agent:
    cfg = settings.transportation_expense
    system_prompt = get_transportation_expense_system_prompt(  # (A) プロンプト生成
        applicant_name=applicant_name,
        application_date=application_date,
        deadline=deadline,
    )
    return create_specialist_agent(                            # (B) Agent 組み立て
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[calculate_transportation_cost, generate_transportation_expense_form],
        agent_id="transportation_expense_agent",
        agent_name="交通費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )
```

---

#### (A) get_transportation_expense_system_prompt() — 申請者専用プロンプトの生成

```python
# prompt/prompt_transportation_expense.py  78〜102行
def get_transportation_expense_system_prompt(
    applicant_name: str,
    application_date: str,
    deadline: str,
) -> str:
    policies = get_transportation_expense_policies(...)   # 社内ルールを取得
    return _TRANSPORTATION_EXPENSE_SYSTEM_PROMPT_TEMPLATE.format(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline=deadline,
        transportation_expense_policies=policies,
    )
```

このファイルにはテンプレート文字列が定義されています。

```python
# prompt/prompt_transportation_expense.py  5〜75行（抜粋）
_TRANSPORTATION_EXPENSE_SYSTEM_PROMPT_TEMPLATE = """\
あなたは交通費精算申請の専門エージェントです。

## コンテキスト情報
- 申請者名: {applicant_name}      ← ここに実際の名前が入る
- 申請日: {application_date}      ← ここに今日の日付が入る
- 申請期限: {deadline}            ← ここに計算済みの期限が入る

## 対話フロー
1. 情報収集（利用日・出発地・目的地・交通手段・利用目的）
2. 交通費計算（calculate_transportation_cost ツールを使用）
3. ルールチェック
4. ドラフト提示（テキストのみ、ツール呼び出し不可）
5. 承認確認
6. 申請書生成（generate_transportation_expense_form ツールを使用）
...
"""
```

`str.format()` で `{applicant_name}` などのプレースホルダーを実際の値に置き換えます。山田さんが申請すれば「申請者名: 山田」と書かれたプロンプトが、鈴木さんなら「申請者名: 鈴木」と書かれたプロンプトが生成されます。

```
テンプレート（固定）+ 申請者ごとの情報（動的） = 申請者専用プロンプト
```

これにより LLM は最初から申請者の文脈を把握した状態で動き始めます。プロンプトには対話フロー（1〜6のステップ）や使えるツールの説明も含まれており、LLM の振る舞い全体を制御しています。

---

#### (B) create_specialist_agent() — Agent の組み立て

```python
# base_agent.py  46〜102行
def create_specialist_agent(
    session_id, system_prompt, tools, agent_id, agent_name,
    window_size, max_iterations, max_attempts, initial_delay, max_delay,
) -> Agent:
    session_manager = SessionManagerFactory.create(session_id)
    approval_hook = HumanApprovalHook(target_tools=_APPROVAL_TARGET_TOOLS)
    loop_hook = LoopControlHook(max_iterations=max_iterations, agent_name=agent_name)

    return Agent(
        model=ModelConfig.get_model(),
        system_prompt=system_prompt,
        tools=tools,
        ...
        hooks=[approval_hook, loop_hook],
        session_manager=session_manager,
    )
```

`create_specialist_agent()` は `base_agent.py` に定義された**共通ファクトリー関数**です。交通費・一般経費など複数の専門エージェントが同じ手順で `Agent` を組み立てるため、共通処理をここに集約しています。

`_build_transportation_expense_agent()` から渡される引数の役割を整理します。

| 引数 | 渡している値 | 意味 |
|------|-------------|------|
| `system_prompt` | `get_transportation_expense_system_prompt()` の結果 | LLMへの指示（対話フロー・ルール） |
| `tools` | `[calculate_transportation_cost, generate_transportation_expense_form]` | LLMが使える機能 |
| `cfg.window_size` | 設定ファイルの値 | 保持する会話履歴の件数 |
| `cfg.max_iterations` | 設定ファイルの値 | LoopControlHook の上限回数 |
| `cfg.max_attempts` | 設定ファイルの値 | API失敗時のリトライ回数 |
| `cfg.initial_delay` | 設定ファイルの値 | リトライの初期待機秒数 |
| `cfg.max_delay` | 設定ファイルの値 | リトライの最大待機秒数 |

`tools` にはオーケストレーターと異なり「別のエージェント」ではなく**実際の処理を行うPython関数**が渡されます。

| ツール | 役割 |
|--------|------|
| `calculate_transportation_cost` | 出発地・目的地・交通手段から運賃を計算 |
| `generate_transportation_expense_form` | 収集した情報から申請書ファイルを生成 |

また `create_specialist_agent()` 内では `HumanApprovalHook` も追加されます。これは申請書生成（`generate_transportation_expense_form`）を実行する前に人間の承認を求めるフックで、誤った申請書が生成されないよう保護しています。`LoopControlHook` は `orchestrator_agent.py` と同様に無限ループを防ぐ役割です。

---

## まとめ：このファイルの2層構造

```
① @tool デコレータ付き公開関数
   transportation_expense_agent()
   ─────────────────────────────────────────────────────
   役割  : オーケストレーターに「ツール」として見せる窓口
   処理  : invoke_specialist_agent() に委譲するだけ
   ポイント: docstring がLLMの判断材料になる

② プライベート関数
   _build_transportation_expense_agent()
   ─────────────────────────────────────────────────────
   役割  : 交通費専用の Agent インスタンスを組み立てる
   処理  : 申請者情報をプロンプトに埋め込み、専用ツールを設定する
   ポイント: 呼び出すたびに新しい Agent を生成（申請者ごとに独立）
```

オーケストレーターからは「ただの関数」に見えますが、内部では**もう一段階のLLMエージェントが動いている**のがAgent as Tools パターンの本質です。
