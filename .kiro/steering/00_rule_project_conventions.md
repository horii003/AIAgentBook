---
inclusion: fileMatch
fileMatchPattern: ".kiro/artifact-workflow/prompts/06_code-generation/**"
---

# プロジェクト共通規約

## R6. 技術スタック

| カテゴリ | 技術 | バージョン要件 |
|:---|:---|:---|
| 言語 | Python | 3.10以上（型ヒント・match文対応） |
| AIエージェントフレームワーク | AWS Strands SDK | strands-agents >= 0.1.0 |
| エージェントツール | AWS Strands Tools | strands-agents-tools >= 0.1.0 |
| エージェントビルダー | AWS Strands Builder | strands-agents-builder >= 0.1.0 |
| LLMプロバイダ | Amazon Bedrock (boto3) | boto3 >= 1.34.0 |
| データバリデーション | Pydantic | pydantic >= 2.0.0 |
| 設定管理 | pydantic-settings | pydantic-settings >= 2.0.0 |
| AIエージェント評価フレームワーク | strands-agents-evals | strands-agents-evals >= 0.1.0 |
| テストフレームワーク | pytest | pytest >= 7.4.0 |
| カバレッジ計測 | pytest-cov | pytest-cov >= 4.1.0 |
| 環境変数管理 | python-dotenv | python-dotenv >= 1.0.0 |
| 日付処理 | python-dateutil | python-dateutil >= 2.8.2 |
| ロギング | logging（標準ライブラリ） | - |

### 追加パッケージの例（業務要件に応じて選択）

| カテゴリ | 技術 | バージョン要件 | 用途 |
|:---|:---|:---|:---|
| Excel生成 | openpyxl | openpyxl >= 3.1.0 | Excel形式の帳票出力 |

---

## R7. 命名規則

| 対象 | 規則 | 例 |
|:---|:---|:---|
| ファイル名 | snake_case | `search_tools.py`, `error_handler.py` |
| クラス名 | PascalCase | `ErrorHandler`, `OutputGenerator` |
| 関数名 | snake_case | `search_data`, `load_master_data` |
| メソッド名 | snake_case | `generate_session_id`, `get_model` |
| プライベートメソッド | `_`接頭辞 + snake_case | `_get_applicant_info`, `_initialize_user_info` |
| プライベートインスタンス変数 | `_`接頭辞 + snake_case | `self._error_handler`, `self._session_id` |
| モジュールレベルプライベート変数 | `_`接頭辞 + snake_case | `_error_handler`, `_storage_dir` |
| 定数（クラス変数） | UPPER_SNAKE_CASE | `DEFAULT_MODEL_ID`, `COLUMN_WIDTHS` |
| 定数（モジュールレベル） | UPPER_SNAKE_CASE | `ORCHESTRATOR_SYSTEM_PROMPT` |
| エージェントID | snake_case | `orchestrator_agent`, `specialist_a_agent` |
| エージェント表示名 | 日本語 | `受付窓口エージェント`, `{ドメインA}エージェント` |

---

## R8. 言語ポリシー

| 対象 | 使用言語 | 備考 |
|:---|:---|:---|
| 識別子（変数名、関数名、クラス名） | 英語 | snake_case / PascalCase |
| モジュールdocstring | 日本語 | ファイル先頭の説明 |
| クラスdocstring | 日本語 | クラスの目的と機能説明 |
| メソッド/関数docstring | 日本語 | Args, Returns, Raisesの説明も日本語 |
| インラインコメント | 日本語 | セクション区切りコメント含む |
| ユーザー向けメッセージ（print, input） | 日本語 | ユーザーとのインタラクション |
| ログメッセージ | 日本語 | ErrorHandler経由の全ログ |
| エラーメッセージ（ユーザー向け） | 日本語 | handle_*メソッドの戻り値 |
| システムプロンプト | 日本語 | LLMへの指示テキスト |
| JSONデータファイルのキー | 英語 | `name`, `value`, `type` 等 |

---

## R9. 共通コーディングパターン

### R9.1 エラーハンドリングパターン

`ErrorHandler` クラスは全メソッドが `@staticmethod` であり、インスタンス化不要で `ErrorHandler.handle_xxx()` として直接呼び出す。

- **インスタンス不要**: `ErrorHandler` はインスタンスを作成せず、クラスメソッドとして呼び出す
- **エラー処理の委譲**: エラー種別ごとの `handle_*` メソッドを呼び出し、戻り値（ユーザー向けメッセージ文字列）を利用する
- **エラーハンドリングの階層**: `LoopLimitError` → `Exception` の順でキャッチする
- **ツール関数のエラー返却**: 辞書形式で返す。例外を再送出しない。**キー名は出力Pydanticモデルのフィールド名と必ず一致させる**（`success`, `error_message` 等）。`message` 等の独自キーは使用しない
- **ドメイン固有のエラーハンドラ**: 業務要件に応じて `handle_{domain}_error()` メソッドを `ErrorHandler` に追加する
- **複数 `except` 節の統合**: 同一の処理を実行する複数の `except` 節は禁止。例外クラスをタプルでまとめるか、共通の親クラス（`Exception`）1つに統合する。`PermissionError`・`IOError` はどちらも `OSError` のサブクラスであり、`except Exception` 1つで包括できる

### R9.2 ログ出力パターン

各モジュールのモジュールレベルで `_logger = logging.getLogger(__name__)` を定義し、直接 `logging` モジュールを呼び出す。`ErrorHandler` はユーザー向けメッセージ文字列の生成のみを担当し、ログ出力は行わない。

- **ロガーの定義**: `_logger = logging.getLogger(__name__)` は、そのモジュール内に `_logger.info` / `.warning` / `.error` 等の呼び出しが存在する場合にのみモジュール先頭で定義する。ログ出力を行わない薄いラッパーモジュールには定義しない
- **ログレベルの使い分け**:
  - `_logger.debug`: 開発時のデバッグ情報
  - `_logger.info`: 正常処理の記録（処理開始、処理完了、データ読み込み成功等）
  - `_logger.warning`: 注意が必要な状態（ループ制限到達等）
  - `_logger.error`: エラー発生（`exc_info=True` でスタックトレースを付与）
- **スタックトレース出力**: `exc_info=True` パラメータで制御。バリデーションエラー、データ読み込みエラー、予期しないエラーでは有効にする

### R9.3 バリデーションパターン

外部から受け取るデータは全てPydanticモデルでバリデーションを行う。

- **バリデーション実行タイミング**: ツール関数の入口、エージェント呼び出し時の`invocation_state`受取時
- **共通バリデータ関数**: 複数モデルで共有するバリデータを関数として定義し、`field_validator` で各モデルに適用する。業務要件に応じて追加のバリデータを定義する
- **バリデーションエラー処理**: `ValidationError` をキャッチし、`ErrorHandler.handle_validation_error()` に委譲
- **バリデーション済みデータの利用**: バリデーション後はPydanticモデルのインスタンス属性またはmodel_dump()を通じてデータにアクセスする

#### R9.3.1 モデルカテゴリと用途

| カテゴリ | 用途 | 定義元 | 利用先 |
|:---|:---|:---|:---|
| マスタデータモデル | `data/`配下のJSONファイルの型保証 | JSONデータ構造に対応 | `tools/{domain}_tools.py` |
| ツール入力モデル | ツール関数の入力パラメータの型保証 | ツール関数の引数に対応 | `tools/{domain}_tools.py` |
| エージェント状態モデル | `invocation_state`の型保証 | `models/data_models.py` に `InvocationState` クラスとして定義 | `agents/orchestrator_agent.py`（生成元）, `tools/`（参照先） |
| 出力生成モデル | 出力ファイル生成時のデータ型保証 | 出力内容の構造に対応 | `tools/output_generator.py` |

**InvocationState の定義例（`models/data_models.py`）:**

```python
class InvocationState(BaseModel):
    """オーケストレーターから子エージェントへ渡す共有状態

    invocation_state はLLMのコンテキストウィンドウを消費せず、
    ツール関数内でのみ参照できる（@tool(context=True) + tool_context.invocation_state）。
    """
    user_name: str = Field(..., description="申請者名")
    request_date: str = Field(..., description="申請日（YYYY-MM-DD）")
    session_id: str = Field(..., description="セッションID（子エージェントのファクトリで消費）")
```

**【禁止】未使用モデルの定義**: 定義したモデルは対応するツール関数内で実際に使用すること。ツール出力モデル（`XxxOutput`）はツール戻り値の構築に、マスタデータモデルはデータ読み込み時に使用する。使用されないモデルはデッドコードとして削除する。

#### R9.3.2 Field定義パターン

| パターン | 用途 | 例 |
|:---|:---|:---|
| `Field(..., description="説明")` | 必須フィールド | `name: str = Field(..., description="名称")` |
| `Field(None, description="説明")` | 任意フィールド（デフォルトNone） | `notes: Optional[str] = Field(None, description="備考")` |
| `Field(..., min_length=1)` | 空文字禁止 | `name: str = Field(..., min_length=1, description="名称")` |
| `Field(..., gt=0)` | 正の数値のみ | `amount: float = Field(..., gt=0, description="金額")` |
| `Field(..., ge=0)` | 0以上の数値 | `cost: float = Field(..., ge=0, description="費用")` |
| `Literal[...]` | 許可値の列挙 | `category: Literal["A", "B", "C"]` |

#### R9.3.3 バリデーターの適用パターン

| パターン | 用途 | 例 |
|:---|:---|:---|
| 共通バリデーター関数の適用 | 複数モデルで共有するバリデーション | `_validate_xxx = field_validator("field_name", mode="before")(classmethod(validate_xxx))` |
| クラスメソッドバリデーター | モデル固有のバリデーション | `@field_validator("items")` + `@classmethod` |

> **ラムダラッパーの禁止**: `classmethod(lambda cls, v: validate_xxx(v))` のように既存の共通バリデーター関数を単純にラムダで包むのは冗長。`classmethod(validate_xxx)` として直接渡すこと。

#### R9.3.4 バリデーション実行タイミング

| タイミング | 実行箇所 |
|:---|:---|
| ツール関数の入口 | `tools/{domain}_tools.py` |
| invocation_state受取時 | `agents/orchestrator_agent.py` |
| invocation_stateの再バリデーション | `tools/output_generator.py` |
| マスタデータ読み込み時 | `tools/{domain}_tools.py` |

### R9.4 デコレータの使い分け

AWS Strandsフレームワークのツールデコレータは以下の基準で使い分ける。

| デコレータ | 使用条件 | 例 |
|:---|:---|:---|
| `@tool` | `invocation_state` やツールコンテキストを参照しないツール | `search_data`, `calculate_value` |
| `@tool(context=True)` | `invocation_state` を参照する、または `ToolContext` が必要なツール | `specialist_a_agent`, `output_generator` |

- `@tool(context=True)` を使用する場合、関数の最後の引数に `tool_context: ToolContext` を追加する
- デコレータは関数シグネチャの直前に配置する

### R9.5 Agent()コンストラクタの共通パラメータ

全エージェントは `strands.Agent()` コンストラクタで以下の共通パラメータを設定する。

#### R9.5.1 Agent()パラメータ一覧

```python
from strands import Agent, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager

agent = Agent(
    # ---- 必須パラメータ ----
    model=ModelConfig.get_model(),
    system_prompt=SYSTEM_PROMPT,       # str: システムプロンプト（prompt/モジュールから取得）
    tools=[tool_a, tool_b],            # List: エージェントが利用するツール関数のリスト

    # ---- エージェント識別パラメータ（全エージェントで必ず設定すること） ----
    agent_id="agent_id_snake_case",    # str: エージェントの一意識別子（snake_case）
    name="エージェント表示名",            # str: エージェントの日本語表示名（ログ・デバッグで識別）
    description="エージェントの役割説明",  # str: Agent as Tools 時に LLM への説明文となる

    # ---- 会話管理パラメータ ----
    conversation_manager=SlidingWindowConversationManager(
        window_size=20,                # int: 保持するメッセージ数（下記サイズ目安表参照）
        should_truncate_results=True,  # bool: ウィンドウ超過時に結果を切り詰め（全エージェント共通: True）
        per_turn=False                 # bool: メッセージ単位でカウント（全エージェント共通: False）
    ),

    # ---- ストリーミング制御 ----
    callback_handler=None,             # None: ストリーミング出力を無効化（全エージェント共通）

    # ---- リトライ戦略 ----
    retry_strategy=ModelRetryStrategy(
        max_attempts=6,                # int: モデル呼び出しの最大リトライ回数（全エージェント共通: 6）
        initial_delay=4,               # int: 指数バックオフの初期遅延秒数（全エージェント共通: 4）
        max_delay=240                  # int: 指数バックオフの最大遅延秒数（全エージェント共通: 240）
    ),

    # ---- セッション管理 ----
    session_manager=session_manager,   # FileSessionManager: SessionManagerFactoryで作成

    # ---- フック ----
    hooks=[loop_control_hook]          # List[HookProvider]: 下記フック構成表参照
)
```

#### R9.5.2 ModelConfig.get_model() の内部パラメータ

`config/model_config.py` の `ModelConfig.get_model()` が返す `BedrockModel` の構成：

```python
BedrockModel(
    model_id=cls.DEFAULT_MODEL_ID,       # str: LLMモデルID（R10参照）
    guardrail_id=cls.GUARDRAIL_ID,       # str: ガードレールID（R10参照）
    guardrail_version=cls.GUARDRAIL_VERSION,  # str: ガードレールバージョン
    guardrail_trace="enabled"            # str: ガードレールトレース（全エージェント共通: "enabled"）
)
```

#### R9.5.3 ウィンドウサイズの目安

| エージェント種別 | window_size | 理由 |
|:---|:---|:---|
| オーケストレーター | 30（大） | 複数の専門エージェントとのやり取りを保持する必要があるため |
| 専門エージェント（複雑な処理） | 20（中） | 複数ステップの情報収集・処理を行うため |
| 専門エージェント（単純な処理） | 15（小） | 特定タスクに集中した短い対話のため |

#### R9.5.4 フック構成

| エージェント種別 | hooks | 理由 |
|:---|:---|:---|
| オーケストレーター | `[LoopControlHook]` | ループ制御のみ（出力生成は専門エージェントが担当） |
| 専門エージェント（出力生成あり） | `[HumanApprovalHook, LoopControlHook]` | 出力前の人間承認 + ループ制御 |
| 専門エージェント（出力生成なし） | `[LoopControlHook]` | ループ制御のみ |

#### R9.5.5 エージェント種別ごとのパラメータ差分

全エージェントで共通のパラメータ（`model`, `callback_handler`, `retry_strategy`, `should_truncate_results`, `per_turn`）を除き、エージェント種別ごとに異なるパラメータは以下の通り：

| パラメータ | オーケストレーター | 専門エージェント |
|:---|:---|:---|
| `system_prompt` | 定数（`ORCHESTRATOR_SYSTEM_PROMPT`） | 定数または動的生成関数 |
| `tools` | 専門エージェントのツール関数 | ドメイン固有ツール + 出力生成ツール |
| `agent_id` | `"orchestrator_agent"` | `"{specialist_name}_agent"` |
| `name` | `"受付窓口エージェント"` 等 | `"{ドメイン}エージェント"` 等 |
| `description` | 振り分け役割の説明 | ドメイン固有処理の説明 |
| `window_size` | 30 | 15〜20 |
| `hooks` | `[LoopControlHook]` | `[HumanApprovalHook, LoopControlHook]` |
| `session_manager` | `self._session_manager`（インスタンス変数） | ファクトリ関数内で都度作成 |

### R9.6 invocation_stateとagent()呼び出しパターン

`Agent()` コンストラクタで生成したエージェントインスタンスを実行する際のパラメータを定義する。

#### R9.6.1 invocation_stateとは

`invocation_state` は `ToolContext` を通じてアクセスできる辞書で、エージェント呼び出し時に渡されたコンテキスト情報を保持する。

- **LLMのプロンプトには含まれない**（コンテキストウィンドウを消費しない）
- **ツール関数の内部でのみ参照できる**（`@tool(context=True)` + `tool_context.invocation_state`）
- **リクエスト単位で有効**（セッションをまたがない）
- 機密情報やシステム内部情報の受け渡しに適している

#### R9.6.2 データの受け渡しアプローチの使い分け

| アプローチ | 用途 | 例 |
|:---|:---|:---|
| ツールパラメータ | LLMが推論・判断して渡すデータ | 検索クエリ、ファイルパス、ユーザーの回答 |
| `invocation_state` | プロンプトに含めたくないが動作に影響するコンテキスト | ユーザーID、セッションID、申請日 |
| クラスベースツール | リクエスト間で変わらない設定 | APIキー、DB接続文字列 |

#### R9.6.3 ツール関数内でのinvocation_stateの参照

`@tool(context=True)` を付けたツール関数内で `tool_context.invocation_state` から辞書として取得する：

```python
from strands import tool, ToolContext

@tool(context=True)
def output_generator(data: list, tool_context: ToolContext) -> dict:
    """出力ファイルを生成する。

    Args:
        data: 出力データのリスト
    """
    # invocation_stateからコンテキスト情報を取得（.get()で安全にアクセス）
    user_name = tool_context.invocation_state.get("user_name")
    request_date = tool_context.invocation_state.get("request_date")
    # ... 出力生成処理 ...
```

| 参照方法 | 説明 |
|:---|:---|
| `tool_context.invocation_state` | 辞書全体を取得 |
| `tool_context.invocation_state.get("key")` | 安全にキーを取得（存在しない場合は `None`） |
| `tool_context.invocation_state["key"]` | キーを取得（存在しない場合は `KeyError`） |

#### R9.6.4 オーケストレーターからのエージェント呼び出し

オーケストレーターの対話ループ内で、ユーザー入力に対してエージェントを実行する：

```python
# invocation_stateをPydanticモデルでバリデーションしてから渡す
invocation_state = InvocationState(
    user_name=self._user_name,
    request_date=datetime.now().strftime("%Y-%m-%d"),
    session_id=self._session_id
)

response = self.agent(
    user_input,                                  # str: ユーザーからの入力テキスト
    invocation_state=invocation_state.model_dump()  # dict: Pydanticモデルを辞書に変換して渡す
)
```

| パラメータ | 型 | 説明 |
|:---|:---|:---|
| 第1引数（位置引数） | `str` | ユーザーからの入力テキスト |
| `invocation_state` | `dict` | エージェント間で共有する状態データ。Pydanticモデルの `model_dump()` で辞書化して渡す |

#### R9.6.5 専門エージェント（Agent as Tool）からのエージェント呼び出し

`@tool(context=True)` でラップされた専門エージェントのツール関数内で、子エージェントを実行する：

```python
# invocation_stateから必要な情報のみを抽出して子エージェントに伝播
state = tool_context.invocation_state  # オーケストレーターから渡されたstate

# ファクトリ関数でエージェント生成
agent = _get_specialist_a_agent(session_id=state["session_id"])

# 子エージェントにはsession_idを含めず、業務に必要な情報のみを伝播
child_invocation_state = {
    "user_name": state["user_name"],
    "request_date": state["request_date"]
}

response = agent(
    query,                                      # str: オーケストレーターからの質問・指示
    invocation_state=child_invocation_state      # dict: 子エージェント用の状態データ
)
```

#### R9.6.6 invocation_stateの伝播ルール

| 段階 | 伝播の流れ | 渡すフィールド | 説明 |
|:---|:---|:---|:---|
| ① | オーケストレーター → オーケストレーターagent() | 全フィールド（`model_dump()`） | Pydanticモデルを辞書化して渡す |
| ② | 専門エージェントツール関数 → 子agent() | 業務に必要なフィールドのみ | `session_id`はファクトリ関数で消費済みのため除外 |
| ③ | 専門エージェント内のツール | `tool_context.invocation_state`で参照 | `@tool(context=True)`のツールのみアクセス可能 |

### R9.7 Agent as Toolsパターン

専門エージェントはオーケストレーターからツールとして呼び出される。

- **ビルド関数**: `_build_{エージェント名}_agent(session_id, applicant_name, application_date, deadline)` という命名の関数でエージェントインスタンスを生成する
- **共通ファクトリ**: `agents/base_agent.py` の `create_specialist_agent(...)` を使ってエージェントを生成する（Session/Hook/LoopControlHook の個別作成は不要）
- **共通呼び出しラッパー**: `agents/base_agent.py` の `invoke_specialist_agent(...)` を使って呼び出す（invocation_state の取得・deadline 計算・エージェント呼び出し・例外処理を共通化）
- **ツール関数化**: `@tool(context=True)` でデコレートした関数内で `invoke_specialist_agent(...)` を呼び出す
- **エラーハンドリング**: `LoopLimitError` → `Exception` の2層構造でキャッチし、`ErrorHandler` の対応 static メソッドに委譲。戻り値は文字列（エラーメッセージ）

```python
from agents.base_agent import create_specialist_agent, invoke_specialist_agent

def _build_specialist_a_agent(
    session_id: str,
    applicant_name: str,
    application_date: str,
    deadline: str,
) -> Agent:
    cfg = settings.specialist_a
    system_prompt = get_specialist_a_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline=deadline,
    )
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[tool_function_1, output_generator],
        agent_name="専門エージェントAの表示名",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )


@tool(context=True)
def specialist_a_agent(query: str, tool_context: ToolContext) -> str:
    """専門エージェントAツール"""
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-00X",
        deadline_months=settings.specialist_a.deadline_months,
        build_agent=_build_specialist_a_agent,
    )
```

---

## R10. 共通設定値

| 設定項目 | 値 | 適用対象 | 備考 |
|:---|:---|:---|:---|
| LLMモデルID | `{geography}.{provider}.{model-id}:{version}` | 全エージェント | jp.anthropic.claude-sonnet-4-5-20250929-v1:0 |
| ガードレールID | `{guardrail_id}` | 全エージェント | コンテンツポリシー制御用（任意） |
| ガードレールバージョン | `DRAFT` | 全エージェント | ドラフトまたは公開バージョン |
| ガードレールトレース | `enabled` | 全エージェント | トレース有効 |
| 最大ループ回数 | `10` | 全エージェント | ReActループの上限 |
| リトライ最大試行回数 | `6` | 全エージェント | モデル呼び出しのリトライ回数 |
| リトライ初期遅延 | `4`秒 | 全エージェント | 指数バックオフの初期値 |
| リトライ最大遅延 | `240`秒 | 全エージェント | 指数バックオフの上限 |
| ストリーミング | 無効（`callback_handler=None`） | 全エージェント | エンドユーザー向けアプリのため |
| 会話履歴の切り詰め | `should_truncate_results=True` | 全エージェント | ウィンドウ超過時に結果を切り詰め |
| 会話履歴のターン単位 | `per_turn=False` | 全エージェント | メッセージ単位でカウント |
| ログフォーマット | `%(asctime)s [%(levelname)s] %(name)s - %(message)s` | main.py | 全ログ出力に適用 |
| ログファイルエンコーディング | `utf-8` | main.py | 日本語対応 |
| ログファイルパス（INFO以上） | `logs/app.log` | main.py | アプリログ出力先（RotatingFileHandler: 10MB × 5世代） |
| ログファイルパス（ERROR以上） | `logs/error.log` | main.py | エラーログ出力先（RotatingFileHandler: 10MB × 5世代） |
| Strandsイベントループログレベル | `WARNING` | main.py | 過剰なデバッグ出力を抑制 |
| Excel出力先 | `output/` | 出力生成ツール | 実行時自動作成 |
| セッション保存先 | `storage/sessions/` | セッション管理 | プロジェクトルートからの相対パス |

### カスタマイズガイド

- LLMモデルIDはリージョンとモデルファミリーに応じて変更する
- ガードレールIDはAmazon Bedrockで作成したガードレールに応じて設定する
- 業務要件に応じて固有の設定値（期間制限、金額閾値等）を追加する

---

## R9.8 HookProviderの実装パターン

`HookProvider` を継承してフックを実装する際は、以下のStrands SDK仕様に従う。

### R9.8.1 利用可能なイベントクラス

```python
from strands.hooks import (
    BeforeInvocationEvent,   # エージェント呼び出し開始前
    AfterInvocationEvent,    # エージェント呼び出し完了後
    BeforeModelCallEvent,    # LLMモデル呼び出し前
    AfterModelCallEvent,     # LLMモデル呼び出し後
    BeforeToolCallEvent,     # ツール実行前
    AfterToolCallEvent,      # ツール実行後
)
```

### R9.8.2 register_hooksの実装

フックの登録には `registry.add_callback()` を使用する（`add_hook()` は存在しない）。

```python
def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
    registry.add_callback(BeforeToolCallEvent, self._handle_before_tool_call)
    registry.add_callback(AfterToolCallEvent, self._handle_after_tool_call)
```

### R9.8.3 BeforeToolCallEventの属性

`BeforeToolCallEvent` はツール実行前に発火する。全ツール呼び出しで発火するため、ハンドラー内で対象ツールを必ずフィルタリングすること。

```python
@dataclass
class BeforeToolCallEvent:
    selected_tool: AgentTool | None  # 実行されるツールオブジェクト（ツール検索失敗時はNone）
    tool_use: ToolUse                # ツール呼び出しパラメータ（TypedDict）
    invocation_state: dict           # エージェント呼び出し時のinvocation_state
    cancel_tool: bool | str          # キャンセル制御（デフォルト: False）
```

`ToolUse` の構造（TypedDict）：

```python
class ToolUse(TypedDict):
    name: str        # ツール名
    input: Any       # ツールへの入力パラメータ（dict）
    toolUseId: str   # ツール呼び出しの一意ID
```

アクセス方法：

```python
def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
    tool_name = event.tool_use["name"]          # ツール名
    tool_input = event.tool_use["input"] or {}  # ツール入力パラメータ
    tool_use_id = event.tool_use["toolUseId"]   # ツール呼び出しID

    # 対象ツール以外はスキップ（全ツール呼び出しで発火するため必須）
    if tool_name not in self.target_tools:
        return
```

### R9.8.4 ツール呼び出しのキャンセル方法

`event.cancel()` は存在しない。`event.cancel_tool` にメッセージ文字列を設定してキャンセルする。

```python
# キャンセル: cancel_toolにメッセージを設定する（event.cancel()は存在しない）
event.cancel_tool = "ユーザーによりキャンセルされました。"

# Trueを設定するとStrands標準のキャンセルメッセージが使用される
event.cancel_tool = True
```

### R9.8.5 AfterToolCallEventの属性

```python
@dataclass
class AfterToolCallEvent:
    selected_tool: AgentTool | None  # 実行されたツールオブジェクト
    tool_use: ToolUse                # ツール呼び出しパラメータ
    invocation_state: dict           # エージェント呼び出し時のinvocation_state
    result: ToolResult               # ツール実行結果
    exception: Exception | None      # 例外（正常時はNone）
    cancel_message: str | None       # キャンセルメッセージ（キャンセル時のみ）
```

### R9.8.6 ハンドラー内の重複ロジックのヘルパー化

複数のイベントハンドラーで同一の式（例: `event.tool_use` の null チェックと属性取得）を繰り返す場合は、プライベートヘルパーメソッドに抽出する。

```python
# NG: 同じ null チェック式が複数ハンドラーで重複
def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
    tool_name = event.tool_use["name"] if event.tool_use else "unknown"
    ...

def _handle_after_tool_call(self, event: AfterToolCallEvent) -> None:
    tool_name = event.tool_use["name"] if event.tool_use else "unknown"  # 重複
    ...

# OK: プライベートヘルパーに抽出
def _get_tool_name(self, event) -> str:
    return event.tool_use["name"] if event.tool_use else "unknown"

def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
    tool_name = self._get_tool_name(event)
    ...

def _handle_after_tool_call(self, event: AfterToolCallEvent) -> None:
    tool_name = self._get_tool_name(event)
    ...
```

---

## R9.11 エージェント共通ユーティリティパターン

専門エージェントの生成・呼び出しに共通する処理は `agents/base_agent.py` に集約する。

### R9.11.1 共通ファクトリ関数

`create_specialist_agent(...)` は Session/HumanApprovalHook/LoopControlHook の生成と Agent インスタンスの組み立てを行う。各専門エージェントのビルド関数はこれを呼び出す。

```python
from agents.base_agent import create_specialist_agent

def _build_specialist_a_agent(session_id, applicant_name, application_date, deadline):
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=get_system_prompt(...),
        tools=[tool_a, output_generator],
        agent_name="専門エージェントAの表示名",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )
```

### R9.11.2 共通呼び出しラッパー

`invoke_specialist_agent(...)` は invocation_state の取得・deadline 計算・エージェント呼び出し・例外処理を共通化する。

```python
from agents.base_agent import invoke_specialist_agent

@tool(context=True)
def specialist_a_agent(query: str, tool_context: ToolContext) -> str:
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-00X",
        deadline_months=settings.specialist_a.deadline_months,
        build_agent=_build_specialist_a_agent,
    )
```

### R9.11.3 期限計算

`calculate_deadline(application_date, deadline_months)` は申請日から申請期限を計算して `YYYY-MM-DD` 形式で返す。パース失敗時は `"要確認"` を返す。

---

## R9.12 コード品質ルール

### R9.12.1 ツール関数間の共通処理の抽出（DRY 原則）

複数のツール関数で同一の処理フローが繰り返される場合は、内部ヘルパー関数に抽出する。

典型的な重複パターン:
- `invocation_state` からの情報取得
- `ValidationError` の try/except
- テンプレートファイルの存在確認
- ワークブック読み込み → セル書き込み → ファイル保存

```python
# NG: 同じフローを持つ出力ツール関数が複数存在する
@tool(context=True)
def generate_type_a_form(items: list, tool_context: ToolContext) -> dict:
    applicant_name = tool_context.invocation_state.get("applicant_name", "")
    try:
        validated = TypeAFormInput(applicant_name=applicant_name, items=items)
    except ValidationError as e:
        return {"success": False, "message": ErrorHandler.handle_validation_error(e)}
    if not os.path.exists(_TYPE_A_TEMPLATE):
        return {"success": False, "message": "テンプレートが見つかりません"}
    # ... Excel 書き込み ...

@tool(context=True)
def generate_type_b_form(items: list, tool_context: ToolContext) -> dict:
    applicant_name = tool_context.invocation_state.get("applicant_name", "")  # 重複
    try:
        validated = TypeBFormInput(applicant_name=applicant_name, items=items)
    except ValidationError as e:
        return {"success": False, "message": ErrorHandler.handle_validation_error(e)}  # 重複
    if not os.path.exists(_TYPE_B_TEMPLATE):
        return {"success": False, "message": "テンプレートが見つかりません"}  # 重複
    # ... Excel 書き込み ...

# OK: 共通処理をヘルパーに抽出し、差分（テンプレートパス・行書き込み関数）のみ引数化
def _generate_form(
    template_path: str,
    validated,
    write_detail_rows,
    output_filename: str,
) -> dict:
    """共通フォーム生成処理（テンプレート読み込み → 書き込み → 保存）"""
    ...

@tool(context=True)
def generate_type_a_form(items: list, tool_context: ToolContext) -> dict:
    ...
    return _generate_form(_TYPE_A_TEMPLATE, validated, _write_type_a_rows, "TypeA申請書")
```

同様に、JSON ファイル読み込みパターン（ファイル存在確認 → `open` → `json.load` → エラー処理）が複数ファイルで繰り返される場合は `_load_json_file(path: str)` 等のヘルパーに抽出する。

---

### R9.12.4 モジュールレベルキャッシュパターン

モジュールレベルのキャッシュ変数（リスト・辞書等）の「未ロード」判定に **空コンテナ（`not _data`）を使用してはならない**。空コンテナは「ロード済みだが件数ゼロ」と「未ロード」を区別できないため、論理バグになる。

```python
# NG: 空リストで未ロードを判定している
_data: list = []

if not _data:       # ロード済みで0件でも再ロードが走る
    _load_data()

# OK: 初期化フラグで管理する
_data: list = []
_data_loaded: bool = False

def _load_data() -> tuple[bool, str]:
    global _data, _data_loaded
    # ... ロード処理 ...
    _data_loaded = True
    return (True, "")

if not _data_loaded:    # 未ロード時のみ読み込む
    ok, err_msg = _load_data()
```

`ModelConfig.get_model()` のように「設定に基づいて1回だけ生成すればよいオブジェクト」には `@lru_cache(maxsize=1)` を使う：

```python
from functools import lru_cache

class ModelConfig:
    @classmethod
    @lru_cache(maxsize=1)
    def get_model(cls) -> BedrockModel:
        return BedrockModel(...)
```

---

### R9.12.2 未使用コードの禁止

**未使用インポートの禁止**:
インポートしたシンボルはそのファイル内で必ず使用する。他のモジュールに処理を委譲した結果として不要になったインポート文は削除する。

```python
# NG: calculate_deadline はこのファイル内で使用しない
from agents.base_agent import create_specialist_agent, invoke_specialist_agent, calculate_deadline

# OK: 実際に使用するシンボルのみインポート
from agents.base_agent import create_specialist_agent, invoke_specialist_agent
```

**未使用引数の禁止**:
関数のシグネチャに定義した引数は関数本体内で必ず使用する。プロンプト生成関数（`get_xxx_system_prompt`）の場合は、引数とテンプレートの `{placeholder}` を一対一で対応させること。テンプレートに対応するプレースホルダーがない引数は削除し、シグネチャにない `{placeholder}` は追加する。

```python
# NG: applicant_name をシグネチャに持つがテンプレート内に {applicant_name} が存在しない
def get_specialist_system_prompt(applicant_name: str, application_date: str, ...) -> str:
    return _TEMPLATE.format(
        application_date=application_date,
        # applicant_name が捨てられている
    )

# OK: 使用しない引数は削除するか、テンプレートに {applicant_name} を追加する
def get_specialist_system_prompt(application_date: str, ...) -> str:
    return _TEMPLATE.format(application_date=application_date, ...)
```

---

### R9.12.3 ビジネスルール値の設定ファイル一元管理

ポリシー関数（`get_xxx_policies()`）やシステムプロンプト文言にビジネスルールの具体的な数値（期限月数・金額閾値等）をハードコードしない。`settings.py` で一元管理し、ポリシー関数の引数として受け取って動的に展開する。

```python
# NG: ポリシー文言に数値をハードコード
def get_domain_a_policies() -> str:
    return """
    - BRL-XX: 申請期限は経費発生日から3ヶ月以内
    - BRL-YY: 合計が10,000円を超える場合は上長承認が必要
    """

# OK: 設定値を引数で受け取り動的展開
def get_domain_a_policies(deadline_months: int, approval_threshold: int) -> str:
    return f"""
    - BRL-XX: 申請期限は経費発生日から{deadline_months}ヶ月以内
    - BRL-YY: 合計が{approval_threshold:,}円を超える場合は上長承認が必要
    """

# 呼び出し側（プロンプト生成関数またはエージェントビルド関数）:
get_domain_a_policies(
    deadline_months=settings.domain_a.deadline_months,
    approval_threshold=settings.domain_a.approval_threshold,
)
```

設定値が変わった場合は `settings.py` の 1 箇所を修正するだけで、ポリシー文言・プロンプト・バリデーションロジックすべてに自動的に反映される。

---

## R9.9 ツール関数のdocstringとtool spec

### R9.9.1 tool spec自動生成の制約

Strandsの `@tool` デコレータは関数シグネチャとdocstringからtool spec（JSON Schema）を自動生成し、LLMに渡す。LLMはこのtool specを手がかりにツール呼び出しのパラメータを構築する。

ただし、`list` 等の構造型パラメータは内部構造（要素のプロパティ）がtool specに反映されず空になる。LLMがフィールド名を正しく認識できるよう、docstringの `Args:` セクションに要素構造を明記すること。

### R9.9.2 構造型パラメータの記述ルール

`list` や `dict` など内部に構造を持つパラメータは、要素のフィールド名・型・必須/任意をdocstringに展開して記述する。フィールド名はPydanticモデルの定義と完全一致させること。

```python
@tool(context=True)
def generate_output(records: list, tool_context: ToolContext) -> dict:
    """出力ファイルを生成する。

    Args:
        records: データのリスト。各要素は以下のフィールドを持つ辞書:
            - field_a (str): 説明【必須】
            - field_b (int): 説明【必須】
            - field_c (str|null): 説明【任意、省略可】
        tool_context: ツールコンテキスト（invocation_stateを含む）
    """
```

---

## R10. 環境変数の規約

### R10.1 `.env.template` の定義

プロジェクトルートに `.env.template` を配置し、アプリケーション動作に必要な環境変数の一覧を定義する。
`.env` ファイルは `.env.template` をコピーして作成し、実際の値を設定する。

### R10.2 必須環境変数

| 環境変数名 | 用途 | 設定例 |
|:---|:---|:---|:---|
| `LOG_LEVEL` | ログ出力レベル（DEBUG / INFO / WARNING / ERROR / CRITICAL） | `INFO` |
| `AWS_ACCESS_KEY_ID` | AWS認証用アクセスキーID | — |
| `AWS_SECRET_ACCESS_KEY` | AWS認証用シークレットアクセスキー | — |
| `AWS_DEFAULT_REGION` | AWSデフォルトリージョン | `ap-northeast-1` |
| `GUARDRAIL_ID` | Amazon Bedrockガードレールの識別子 | — |
| `GUARDRAIL_VERSION` | Amazon Bedrockガードレールのバージョン | `DRAFT` |

### R10.3 `.env` ファイルの作成手順

1. `.env.template` をコピーして `.env` ファイルを作成する
2. `.env` ファイルを開き、利用者独自の設定値（AWS認証情報・ガードレールID等）を入力する

### R10.4 運用ルール

- `.env` ファイルは `.gitignore` に登録し、リポジトリにコミットしない
- `.env.template` は値を空欄またはデフォルト値のみ記載し、秘密情報を含めない
- アプリケーション起動時に `python-dotenv` の `load_dotenv()` で `.env` ファイルを読み込む
- 環境変数の参照は `os.getenv("変数名", "デフォルト値")` で行う

---

## R11. テストの規約

| 項目 | ルール |
|:---|:---|
| テストディレクトリ | `tests/unit/`（単体）、`tests/integration/`（結合） |
| テストファイル命名 | `test_{対象モジュール名}.py` |
| テストクラス命名 | `Test{対象クラス名}` |
| テスト関数命名 | `test_{テスト内容}` |

### R11.1 単体テスト

各モジュール（機能単位）ごとに独立したテストファイルを作成する。
- テスト観点は対応する設計書の「テスト観点」セクションを参照する

### R11.2 結合テスト

複数モジュールを組み合わせた連携動作を検証するテストファイルを作成する。
- モジュールの依存関係は「00_rule_directory_structure.md内のR3. ファイル間の依存関係ルール」セクションを参照する

---

## RE1. 評価テスト ディレクトリ構成

```
evals/
├── helpers.py                     # 評価共通ヘルパー
├── eval_{evaluation_name}.py      # 評価スクリプト（指標ごとに1ファイル）
└── logs/
    └── reports/                    # 評価レポート出力先（JSON）
```

- 評価スクリプトの命名: `eval_{evaluation_name}.py`
- ログファイル: `evals/logs/eval_{evaluation_name}.log`
- レポートファイル: `evals/logs/reports/eval_{evaluation_name}_report.json`

---

## RE2. helpers.py の責務

helpers.py は「汎用基盤」と「プロジェクト固有」の2セクションで構成する。

### RE2.1 汎用基盤（プロジェクト非依存）

他のAIエージェント評価プロジェクトでもそのまま再利用できる部分。

| 提供するもの | 責務 |
|---|---|
| `telemetry` | `StrandsEvalsTelemetry().setup_in_memory_exporter()` のシングルトン |
| `memory_exporter` | `telemetry.in_memory_exporter`（スパン収集・クリア用） |
| `get_model()` | LLM-as-Judge 用の判定モデル取得（エージェント本体と同一モデルを使用する） |

### RE2.2 プロジェクト固有

評価対象エージェントの構成に依存する部分。プロジェクトごとに実装が変わる。

| 提供するもの | 責務 |
|---|---|
| `patch_human_approval_hook()` | ブロッキングフックの自動承認差し替え |
| エージェント生成関数 | 評価対象エージェントを本番同一構成で初期化 |
| `create_invocation_state()` | 評価用の状態辞書生成 |
| `run_actor_conversation()` | ActorSimulator によるマルチターン会話実行（マルチターン評価時のみ） |

---

## RE3. eval_*.py の構成順序

各評価スクリプトは以下の順序で構成する。

1. docstring（評価の説明）
2. 初期設定（UTF-8 → sys.path → load_dotenv）
3. helpers import → patch 呼び出し（エージェントモジュールより前に実行）
4. その他 import（strands_evals 等）
5. ログ設定・warnings抑制・SDKログ抑制
6. `EVAL_CASES`（テストケース定義）
7. `run_eval_task()`（タスク関数）
8. `main()`（実験実行・レポート保存・表示）
9. `if __name__ == "__main__"`

---

## RE4. テレメトリ管理ルール

### RE4.1 初期化

- テレメトリは helpers.py でモジュールレベルで初期化する（`StrandsEvalsTelemetry().setup_in_memory_exporter()`）
- eval_*.py 側ではテレメトリ初期化を行わない（helpers を import した時点で完了する）

### RE4.2 trace_attributes（必須）

`StrandsInMemorySessionMapper` を使用する場合、Agent 生成時に以下の `trace_attributes` を**必ず**設定すること。これがないと異なるケースのスパンが混在する。

```python
agent = Agent(
    trace_attributes={
        "session.id": case.session_id,
        "gen_ai.conversation.id": case.session_id,
    },
    ...
)
```

### RE4.3 スパン収集パターン

#### シングルターン評価

タスク関数の先頭で `memory_exporter.clear()` → エージェント実行 → `get_finished_spans()` で収集する。

#### マルチターン評価（ActorSimulator 使用時）

`GoalSuccessRateEvaluator` はセッション全体の trajectory を参照してゴール達成を判定する。そのため **会話ループ内で `memory_exporter.clear()` を呼んではならない**。全ターンのスパンを蓄積し、ループ完了後にまとめて Session を構築する。

スパンのケース間混入防止は `run_eval_task` 関数の先頭で `memory_exporter.clear()` を1回だけ呼ぶことで実現する。

```python
# run_eval_task 内
memory_exporter.clear()  # 前ケースのスパン混入防止（ケース開始時に1回のみ）

# run_actor_conversation 内（clear しない）
while user_sim.has_next():
    agent_response = agent(user_message, ...)
    # memory_exporter.clear() は呼ばない — 全ターンのスパンを蓄積する
    user_result = user_sim.act(str(agent_response))
    user_message = str(user_result.structured_output.message)

# ループ完了後にまとめて収集
spans = list(memory_exporter.get_finished_spans())
session = StrandsInMemorySessionMapper().map_to_session(spans, session_id=session_id)
```

### RE4.4 Session 構築

スパン収集完了後に `StrandsInMemorySessionMapper().map_to_session(all_spans, session_id=case.session_id)` で Session を構築する。

---

## RE5. Strands Evals API 利用規約

### RE5.1 Case の構成

```python
Case(
    name="ケース識別名",
    input="ユーザー入力テキスト",
    expected_assertion="アサーション文（GoalSuccessRateEvaluator で使用、任意）",
    metadata={
        "task_description": "テストの目的説明",
        "goal": "ゴール基準 or expected_tool: 期待ツール名",
    },
)
```

- `expected_assertion`: GoalSuccessRateEvaluator に明示的な合否基準を与える。設定すると evaluator はゴールを推論せず、この基準で判定する（本プロジェクトでは利用しない）
- `session_id`: 未指定時は自動生成される UUID

### RE5.2 ActorSimulator

```python
user_sim = ActorSimulator.from_case_for_user_simulator(
    case=case,
    max_turns=10,  # 最大ターン数
)
```

- `has_next()`: 会話を継続すべきか判定（ゴール達成 or ターン上限で False）
- `act(agent_message)`: エージェント応答を受け取り、次のユーザー発話を生成
- `act()` の戻り値: `user_result.structured_output.message`（次の発話）、`user_result.structured_output.reasoning`（シミュレーターの判断理由）
- ゴール達成時にシミュレーターは `<stop/>` トークンを含むメッセージを生成し自動停止する

### RE5.3 評価器一覧（プロジェクトで使用するもの）

| 評価器 | 評価レベル | スコア | 用途 |
|---|---|---|---|
| `ToolSelectionAccuracyEvaluator` | TOOL_LEVEL | 二値（1.0/0.0） | ツール呼び出しごとに選択の妥当性を判定 |
| `GoalSuccessRateEvaluator` | SESSION_LEVEL | 二値（1.0/0.0） | セッション全体でゴール達成を判定 |

その他利用可能な評価器（必要に応じて追加）:
- `HelpfulnessEvaluator`: 応答の有用性（7段階）
- `FaithfulnessEvaluator`: 会話履歴への忠実性（5段階）
- `TrajectoryEvaluator`: ツール呼び出し列全体の評価（ルーブリック）
- `OutputEvaluator`: 最終応答の品質（カスタムルーブリック）

#### RE5.3.1 ToolSelectionAccuracyEvaluator の制約事項

`ToolSelectionAccuracyEvaluator` は LLM-as-Judge がツール選択の妥当性を判定する。判定時に参照される情報はテレメトリスパンから構築された `ToolConfig` オブジェクトだが、**`strands_evals` のマッパー（`StrandsInMemorySessionMapper`）はツール名のみを抽出し、description を伝播しない**（`"description": null` になる）。

そのため、評価 LLM はツール名だけで妥当性を判断する。**ツール名は、その役割が名前だけで一意に推測できるように命名すること**。

| NG（名前だけでは役割が曖昧） | OK（名前だけで役割が明確） |
|---|---|
| `transport_agent` + `expense_agent` | `transportation_expense_agent` + `receipt_expense_agent` |

命名のポイント:
- 複数のツールが類似ドメインを扱う場合、**対象カテゴリの違い**を名前に含める
- 「精算」のような共通動作ではなく、「何の精算か」が分かる名前にする
- 評価 LLM が description なしで正しく判定できるかを基準に命名を検証する

### RE5.4 Experiment と Report

```python
experiment = Experiment(cases=EVAL_CASES, evaluators=[evaluator])
reports = experiment.run_evaluations(task_function)
```

- `task_function(case: Case) -> dict`: `{"output": str, "trajectory": Session}` を返す
- `report.run_display()`: コンソールにスコア・合否・判定理由を表示
- `report.to_dict()`: JSON シリアライズ可能な辞書を返す
- 複数評価器を使う場合: `EvaluationReport.flatten(reports)` で結果を統合可能

---

## RE6. 評価テスト品質基準

- プレースホルダー（`{...}` 形式）がコード内に残っていないこと
- `EVAL_CASES` に設計書記載のすべてのテストケースが含まれていること
- 評価タイプ（シングルターン / マルチターン）が設計書と一致すること
- レポートが `ensure_ascii=False, indent=2` で JSON 保存されること
- Agent 生成時に `trace_attributes` が設定されていること（RE4.2）
- マルチターン評価で `run_actor_conversation` 内では `memory_exporter.clear()` を呼ばず、全ターンのスパンを蓄積していること（RE4.3）
