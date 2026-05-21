# 実装タスク計画

## 共通参照規約
- `.kiro/steering/00_rule_directory_structure.md`
- `.kiro/steering/00_rule_project_conventions.md`

---

## タスク01: データモデル定義

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/データモデル詳細設計.md`
  - `artifacts/05_detailed-design/outputs/交通費計算ツール詳細設計.md`
  - `artifacts/05_detailed-design/outputs/申請書生成ツール詳細設計.md`
  - `artifacts/03_system-design/outputs/バリデーション方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/01_skeleton_data_models.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/models/data_models.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_data_models.py`
- **実装内容**:
  - `InvocationState` モデル: `applicant_name`（str, 必須）、`application_date`（str, 必須）、`session_id`（str, 必須）フィールドを定義
  - `TransportCalculatorInput` モデル: `departure`（str）、`destination`（str）、`transport_type`（Literal）、`travel_date`（str, YYYY-MM-DD）フィールドを定義
  - `TransportCalculatorOutput` モデル: `success`（bool）、`fare`（Optional[int]）、`message`（str）フィールドを定義
  - `TransportItem` ネストモデル: `travel_date`、`departure`、`destination`、`transport_type`、`fare`、`business_purpose` フィールドを定義
  - `TransportReportInput` モデル: `items`（List[TransportItem]）フィールドを定義
  - `ExpenseItem` ネストモデル: `purchase_date`、`store_name`、`item_name`、`expense_category`（Literal）、`amount`（int, ge=0）、`business_purpose` フィールドを定義
  - `ExpenseReportInput` モデル: `items`（List[ExpenseItem]）フィールドを定義
  - `ReportOutput` モデル: `success`（bool）、`file_path`（Optional[str]）、`message`（str）フィールドを定義
  - `TrainRouteRecord` マスタデータモデル: `departure`、`destination`、`fare`（int）フィールドを定義
  - 固定運賃データは `dict[str, int]` 形式で管理（Pydanticモデル不要）
  - 駅名正規化の共通バリデーター関数 `normalize_station_name` を定義し、`TransportCalculatorInput` の `departure`・`destination` に適用
  - 全フィールドに `Field(..., description="説明")` を付与
- **単体テスト内容**:
  - `InvocationState` の正常系バリデーション（全フィールド指定）
  - `TransportCalculatorInput` の正常系・異常系（transport_type 不正値）
  - `ExpenseItem` の expense_category バリデーション（許可値・不正値）
  - `ExpenseItem` の amount フィールド（0以上の正常系、負値の異常系）
  - `TrainRouteRecord` の正常系バリデーション
  - 駅名正規化バリデーター（「渋谷駅」→「渋谷」等の正規化確認）

---

## タスク02: Bedrockモデル設定

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/03_system-design/outputs/システム基本情報.md`
  - `artifacts/05_detailed-design/outputs/ガードレール詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/02_skeleton_model_config.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/config/model_config.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_model_config.py`
- **実装内容**:
  - `ModelConfig` クラスを定義
  - `DEFAULT_MODEL_ID = "jp.anthropic.claude-sonnet-4-5-20250929-v1:0"` を設定
  - `GUARDRAIL_ID` を環境変数 `GUARDRAIL_ID` から `os.getenv` で取得
  - `GUARDRAIL_VERSION = "DRAFT"` を設定
  - `get_model()` クラスメソッドで `BedrockModel` インスタンスを返却（`guardrail_trace="enabled"` を含む）
  - `@lru_cache(maxsize=1)` を `get_model()` に適用してインスタンスをキャッシュ
- **単体テスト内容**:
  - `get_model()` が `BedrockModel` インスタンスを返すこと
  - `get_model()` を複数回呼び出しても同一インスタンスが返ること（キャッシュ確認）
  - `DEFAULT_MODEL_ID` が期待値と一致すること

---

## タスク03: エラーハンドラー

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ハンドラー詳細設計.md`（Part 1: ErrorHandler）
  - `artifacts/03_system-design/outputs/例外処理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/03_skeleton_error_handler.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/handlers/error_handler.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_error_handler.py`
- **実装内容**:
  - `LoopLimitError(RuntimeError)` カスタム例外クラスを定義
    - フィールド: `current_iteration`（int）、`max_iterations`（int）、`agent_name`（str）
    - `__init__` でエージェント名とループ回数を含む日本語メッセージを生成し `super().__init__` に渡す
  - `ErrorHandler` クラスを定義（全メソッドは `@staticmethod`、インスタンス化不要）
  - 以下のメソッドを実装（各メソッドは日本語ユーザー向けメッセージ文字列を返す）:
    - `handle_throttling_error(e)`: APIレート制限エラー
    - `handle_max_tokens_error(e)`: 最大トークン数到達エラー
    - `handle_context_window_error(e)`: コンテキストウィンドウ超過エラー
    - `handle_fare_data_error(e)`: 運賃データ読み込み失敗
    - `handle_calculation_error(e)`: 運賃計算失敗
    - `handle_file_save_error(e)`: Excelファイル保存失敗
    - `handle_validation_error(e)`: Pydanticバリデーション失敗（`e.errors()` でフィールドごとのエラーを解析）
    - `handle_keyboard_interrupt(e=None)`: ユーザーによる中断
    - `handle_loop_limit_error(e)`: ループ上限到達
    - `handle_runtime_error(e=None)`: その他の実行時エラー
    - `handle_unexpected_error(e=None)`: 予期しないエラー
  - ログ出力は一切行わない（呼び出し元が行う）
  - コンストラクタ・インスタンス変数・`logger` は定義しない
- **単体テスト内容**:
  - `LoopLimitError` の初期化（フィールド値・メッセージ内容確認）
  - 各 `handle_*` メソッドが文字列を返すこと
  - `handle_validation_error` が ValidationError のフィールド情報を含むメッセージを返すこと
  - `handle_loop_limit_error` がエージェント名・ループ回数を含むメッセージを返すこと
  - 引数 `None` を渡した場合でもエラーにならないこと（省略可能メソッド）


---

## タスク04: ReActループ制御フック

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ハンドラー詳細設計.md`（Part 2: LoopControlHook）
  - `artifacts/03_system-design/outputs/実行制御方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/04_skeleton_loop_control_hook.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/handlers/loop_control_hook.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_loop_control_hook.py`
- **実装内容**:
  - `LoopControlHook(HookProvider)` クラスを定義
  - `__init__(max_iterations=10, agent_name="Agent")`: `current_iteration = 0` で初期化
  - `register_hooks()`: 以下の6イベントにコールバックを登録
    - `BeforeInvocationEvent` → `on_before_invocation`
    - `BeforeModelCallEvent` → `on_before_model_call`
    - `AfterModelCallEvent` → `on_after_model_call`
    - `BeforeToolCallEvent` → `on_before_tool_call`
    - `AfterToolCallEvent` → `on_after_tool_call`
    - `AfterInvocationEvent` → `on_after_invocation`
  - `on_before_invocation`: `current_iteration = 0` にリセット、INFO ログ出力
  - `on_before_model_call`: 現在のループ回数を INFO ログ出力
  - `on_after_model_call`: `event.exception` が存在する場合はスキップ。カウントインクリメント後、上限到達時は `LoopLimitError(current_iteration, max_iterations, agent_name)` を raise（WARNING ログ出力）
  - `on_before_tool_call`: `_get_tool_name(event)` でツール名取得し INFO ログ出力
  - `on_after_tool_call`: `_get_tool_name(event)` でツール名取得し INFO ログ出力
  - `on_after_invocation`: 合計ループ回数を INFO ログ出力（リセットは行わない）
  - `_get_tool_name(event)`: `event.tool_use["name"] if event.tool_use else "unknown"` を返すヘルパー
- **単体テスト内容**:
  - `on_before_invocation` でカウンターが 0 にリセットされること
  - `on_after_model_call` でカウンターがインクリメントされること
  - `on_after_model_call` で `event.exception` がある場合はスキップされること
  - 上限到達時に `LoopLimitError` が raise されること（agent_name・max_iterations フィールド確認）
  - `_get_tool_name` が `tool_use=None` の場合に "unknown" を返すこと

---

## タスク05: Human-in-the-Loop承認フック

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ハンドラー詳細設計.md`（Part 3: HumanApprovalHook）
  - `artifacts/05_detailed-design/outputs/申請書生成ツール詳細設計.md`（承認対象ツール名）
  - `artifacts/03_system-design/outputs/実行制御方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/05_skeleton_human_approval_hook.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/handlers/human_approval_hook.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_human_approval_hook.py`
- **実装内容**:
  - `HumanApprovalHook(HookProvider)` クラスを定義
  - `APPROVAL_REQUIRED_TOOLS`: `frozenset({"generate_expense_report", "generate_transport_report"})` を設定
  - `__init__(approval_callback, approval_required_tools=None)`: コールバックと対象ツールセットを初期化
  - `register_hooks()`: `BeforeToolCallEvent` に `_on_before_tool_call` を登録
  - `_on_before_tool_call(event)`:
    - `tool_name = event.tool_use.get("name", "") if event.tool_use else ""` でツール名取得
    - `tool_params = event.tool_use.get("input", {}) if event.tool_use else {}` でパラメータ取得
    - `approval_required_tools` に含まれないツールは `return` でスキップ
    - `approval_callback(tool_name, tool_params)` を呼び出し `(approved, feedback)` を受け取る
    - `approved=True`: INFO ログ出力して `return`（ツール実行される）
    - `approved=False`: `_build_cancel_message(tool_name, feedback)` でメッセージ生成し `event.cancel_tool` にセット
  - `_build_cancel_message(tool_name, feedback)`:
    - `feedback == "CANCEL"` または空の場合: 申請中止メッセージを返す
    - それ以外: 修正要望をLLMに伝えて再生成を促すメッセージを返す
  - コールバックシグネチャ: `(tool_name: str, tool_params: dict) -> tuple[bool, str]`
- **単体テスト内容**:
  - 対象外ツールの場合にコールバックが呼ばれないこと
  - `approved=True` の場合に `event.cancel_tool` が設定されないこと
  - `approved=False, feedback="CANCEL"` の場合に `event.cancel_tool` にメッセージが設定されること
  - `approved=False, feedback="修正内容"` の場合に修正要望メッセージが設定されること
  - `approval_required_tools` を明示指定した場合にデフォルトが上書きされること

---

## タスク06: セッション管理

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/セッションマネージャ詳細設計.md`
  - `artifacts/03_system-design/outputs/セッション管理方針.md`
  - `artifacts/03_system-design/outputs/共通設定方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/06_skeleton_session_manager.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/session/session_manager.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_session_manager.py`
- **実装内容**:
  - `SessionManagerFactory` クラスを定義（全メソッドは `@staticmethod`、インスタンス化不要）
  - クラス変数 `DEFAULT_STORAGE_DIR = "storage/sessions"` を定義
  - `generate_session_id(prefix="")`: `datetime.now().strftime("%Y%m%d%H%M%S") + "_" + uuid.uuid4().hex[:8]` 形式で生成。prefix がある場合は `"{prefix}_{timestamp}_{uuid8}"` 形式
  - `get_storage_dir()`: `_storage_dir` キャッシュ確認 → プロジェクトルートからのパス構築 → `os.makedirs(exist_ok=True)` → パス返却
  - `create_session_manager(session_id)`: `get_storage_dir()` でディレクトリ取得し `FileSessionManager(session_id=session_id, storage_dir=storage_dir)` を返却
  - `get_session_path(session_id)`: セッションサブディレクトリパスを返却
- **単体テスト内容**:
  - `generate_session_id()` が `YYYYMMDDHHMMSS_xxxxxxxx` 形式であること
  - `generate_session_id("test")` が `test_YYYYMMDDHHMMSS_xxxxxxxx` 形式であること
  - 同時に2回呼び出しても異なるIDが生成されること
  - `create_session_manager()` が `FileSessionManager` インスタンスを返すこと
  - `get_storage_dir()` がディレクトリを自動作成すること

---

## タスク07: オーケストレーターシステムプロンプト

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/システムプロンプト詳細設計.md`（AG-001 セクション）
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/07_skeleton_prompt_orchestrator.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/prompt/prompt_orchestrator.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_prompt_orchestrator.py`
- **実装内容**:
  - `ORCHESTRATOR_SYSTEM_PROMPT` 定数（静的文字列）を定義
  - プロンプト構成要素（詳細設計書の AG-001 セクションに従う）:
    - 役割定義: 申請受付窓口エージェントとしての役割
    - 申請種別判断ルール（`{application_policies}` プレースホルダーは使用せず、静的定数のためナレッジは別途 `knowledge/application_policies.py` で管理）
    - 振り分け基準: `expense_agent`（経費精算）・`transport_agent`（交通費精算）への振り分け条件
    - 判断不能時の対応: ユーザーへの選択肢提示
    - 対話ルール: 丁寧な日本語、申請者名の確認済み前提
    - エラーハンドリング指示: 専門エージェントからのエラー時の対応
- **単体テスト内容**:
  - `ORCHESTRATOR_SYSTEM_PROMPT` が文字列型であること
  - プロンプトに `expense_agent`・`transport_agent` の振り分け基準が含まれること
  - プロンプトが空でないこと


---

## タスク08: 専門エージェントシステムプロンプト

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/システムプロンプト詳細設計.md`（AG-002, AG-003 セクション）
  - `artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/08_skeleton_prompt_specialist.md`
- **成果物のファイルパス**:
  - `artifacts/06_code-generation/src/prompt/prompt_specialist_expense.py`
  - `artifacts/06_code-generation/src/prompt/prompt_specialist_transport.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_prompt_specialist.py`
- **実装内容**:
  - `prompt_specialist_expense.py`:
    - `_EXPENSE_SYSTEM_PROMPT_TEMPLATE` テンプレート文字列を定義（プレースホルダー: `{applicant_name}`, `{application_date}`, `{deadline_date}`, `{expense_policies}`, `{expense_category_policies}`）
    - `get_expense_system_prompt(applicant_name, application_date, deadline_date, expense_policies, expense_category_policies)` 関数を定義
    - プロンプト構成: 役割定義・処理フロー・業務ルール（`{expense_policies}`）・経費区分判断基準（`{expense_category_policies}`）・エラーハンドリング指示
  - `prompt_specialist_transport.py`:
    - `_TRANSPORT_SYSTEM_PROMPT_TEMPLATE` テンプレート文字列を定義（プレースホルダー: `{applicant_name}`, `{application_date}`, `{deadline_date}`, `{transport_policies}`）
    - `get_transport_system_prompt(applicant_name, application_date, deadline_date, transport_policies)` 関数を定義
    - プロンプト構成: 役割定義・処理フロー・業務ルール（`{transport_policies}`）・駅名正規化指示・エラーハンドリング指示
  - 引数とテンプレートプレースホルダーは一対一で対応させること（未使用引数・未定義プレースホルダー禁止）
- **単体テスト内容**:
  - `get_expense_system_prompt()` が文字列を返すこと
  - `get_transport_system_prompt()` が文字列を返すこと
  - 各関数の戻り値に引数で渡した `applicant_name`・`application_date` が含まれること
  - テンプレートの全プレースホルダーが引数で埋められること（KeyError が発生しないこと）

---

## タスク09: ナレッジ・業務ルール

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ナレッジ・業務ルール詳細設計.md`
  - `artifacts/02_system-requirements/outputs/業務ルール定義.md`
  - `artifacts/01_business-requirements/outputs/業務ルール定義_判断基準定義.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/09_skeleton_policies.md`
- **成果物のファイルパス**:
  - `artifacts/06_code-generation/src/knowledge/application_policies.py`
  - `artifacts/06_code-generation/src/knowledge/transport_policies.py`
  - `artifacts/06_code-generation/src/knowledge/expense_policies.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_policies.py`
- **実装内容**:
  - `application_policies.py`:
    - `get_application_policies()` 関数（引数なし）: 申請種別判断ルール（KN-001）・申請先情報（KN-002）をマークダウン形式で返す
    - 対象申請種別（交通費精算申請・経費精算申請）の判断基準を含む
  - `transport_policies.py`:
    - `get_transport_policies(deadline_months: int, approval_threshold: int)` 関数: 交通費精算業務ルール（KN-003）をマークダウン形式で返す
    - `deadline_months`・`approval_threshold` を f-string で埋め込む（ハードコード禁止）
    - 申請期限チェック・上長承認チェック・対応交通手段・駅名正規化ルールを含む
  - `expense_policies.py`:
    - `get_expense_policies(deadline_months: int, approval_threshold: int)` 関数: 経費精算業務ルール（KN-004）をマークダウン形式で返す
    - `get_expense_category_policies()` 関数（引数なし）: 経費区分判断基準（KN-005）をマークダウン形式で返す
    - 事務用品費・宿泊費・資格精算費・その他経費の4区分を含む
  - 各モジュールは他のモジュールに依存しない（純粋なテキスト返却のみ）
- **単体テスト内容**:
  - 各関数が文字列を返すこと
  - `get_transport_policies(3, 10000)` の戻り値に "3" と "10,000" が含まれること
  - `get_expense_policies(3, 5000)` の戻り値に "3" と "5,000" が含まれること
  - `get_expense_category_policies()` の戻り値に4つの経費区分が含まれること
  - 各関数が空文字を返さないこと

---

## タスク10: ツール実装

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/交通費計算ツール詳細設計.md`
  - `artifacts/05_detailed-design/outputs/申請書生成ツール詳細設計.md`
  - `artifacts/05_detailed-design/outputs/データモデル詳細設計.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
  - `artifacts/03_system-design/outputs/バリデーション方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/10_skeleton_tools.md`
- **成果物のファイルパス**:
  - `artifacts/06_code-generation/src/tools/transport_tools.py`
  - `artifacts/06_code-generation/src/tools/output_generator.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_transport_tools.py`、`artifacts/06_code-generation/src/tests/unit/test_output_generator.py`
- **実装内容**:
  - `transport_tools.py`:
    - モジュールレベルキャッシュ変数 `_train_routes: list`・`_fixed_fares: dict`・`_train_routes_loaded: bool`・`_fixed_fares_loaded: bool` を定義
    - `_load_train_routes()`: `os.path.exists()` で事前チェック後 `./data/train_routes.json` を読み込み `TrainRouteRecord` でバリデーション。戻り値 `tuple[bool, str]`
    - `_load_fixed_fares()`: `os.path.exists()` で事前チェック後 `./data/fixed_fares.json` を読み込み `dict[str, int]` で管理。戻り値 `tuple[bool, str]`
    - `FileNotFoundError` のログレベルは WARNING
    - `@tool(context=True)` で `calculate_transport_fare(departure, destination, transport_type, travel_date, tool_context)` を定義
    - 電車の場合: `_train_routes` から経路検索（存在しない場合は `ValueError`）
    - バス・タクシー・飛行機の場合: `_fixed_fares` から固定運賃取得
    - 申請期限チェック（移動日から3ヶ月以内）は LLM が行うため、ツールは計算のみ担当
    - 戻り値: `{"success": bool, "fare": int|None, "message": str}`
  - `output_generator.py`:
    - `_generate_form(template_path, validated, write_detail_rows, output_filename)` 共通ヘルパー関数を定義（DRY原則）
    - `@tool(context=True)` で `generate_expense_report(items, tool_context)` を定義
      - `tool_context.invocation_state` から `applicant_name`・`application_date` を取得
      - `ExpenseReportInput` でバリデーション
      - `template/経費精算申請書テンプレート.xlsx` を読み込み、所定セルに書き込み
      - `output/経費精算申請書_{YYYYMMDDHHMMSS}.xlsx` に保存
      - 戻り値: `{"success": bool, "file_path": str|None, "message": str}`
    - `@tool(context=True)` で `generate_transport_report(items, tool_context)` を定義
      - `tool_context.invocation_state` から `applicant_name`・`application_date` を取得
      - `TransportReportInput` でバリデーション
      - `template/交通費精算申請書テンプレート.xlsx` を読み込み、所定セルに書き込み
      - `output/交通費精算申請書_{YYYYMMDDHHMMSS}.xlsx` に保存
      - 戻り値: `{"success": bool, "file_path": str|None, "message": str}`
    - セル位置: 申請者名 B3、申請日 B4、明細 A{7+i}〜H{7+i}、合計金額 H{7+n+2}
    - 出力ファイルパスはツール内部で `datetime.now().strftime("%Y%m%d%H%M%S")` から自律生成（LLMパラメータとして受け取らない）
    - ファイル保存エラー時の戻り値: `(False, エラーメッセージ)` のタプル形式（内部メソッド）
- **単体テスト内容**:
  - `_load_train_routes()` の正常系（JSONファイル読み込み成功）
  - `_load_train_routes()` の異常系（ファイル不存在時に `(False, エラーメッセージ)` を返すこと）
  - `calculate_transport_fare` の電車正常系（既存経路）
  - `calculate_transport_fare` の電車異常系（存在しない経路で `success=False`）
  - `calculate_transport_fare` のバス・タクシー・飛行機正常系（固定運賃）
  - `generate_expense_report` の正常系（モックテンプレートを使用）
  - `generate_transport_report` の正常系（モックテンプレートを使用）
  - バリデーションエラー時に `success=False` が返ること

---

## タスク11: オーケストレーターエージェント

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`
  - `artifacts/03_system-design/outputs/マルチエージェント連携設計.md`
  - `artifacts/03_system-design/outputs/セッション管理方針.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
  - `artifacts/03_system-design/outputs/共通設定方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/11_skeleton_orchestrator_agent.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/agents/orchestrator_agent.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_orchestrator_agent.py`
- **実装内容**:
  - `OrchestratorAgent` クラスを定義
  - `__init__(applicant_name, session_id)`: インスタンス変数 `_applicant_name`・`_session_id`・`_session_manager`・`agent` を初期化
  - `_initialize()`:
    - `SessionManagerFactory.create_session_manager(self._session_id)` でセッション管理を作成
    - `LoopControlHook(max_iterations=settings.orchestrator.max_iterations, agent_name="申請受付窓口エージェント")` を作成
    - `Agent(model, system_prompt=ORCHESTRATOR_SYSTEM_PROMPT, tools=[expense_agent, transport_agent], conversation_manager=SlidingWindowConversationManager(window_size=settings.orchestrator.window_size, ...), callback_handler=None, retry_strategy=ModelRetryStrategy(...), hooks=[loop_control_hook], session_manager=self._session_manager)` を生成
  - `run()` メインインタラクションループ:
    - ウェルカムメッセージ表示（詳細設計書の文言に従う）
    - 対話ループ（最大 `settings.orchestrator.max_turn_count` 回）
    - 入力プロンプト: `"\n\n入力内容（終了時はquit）: "`
    - 入力文字数チェック（`settings.orchestrator.max_input_length` = 500文字超でエラー）
    - 終了コマンド（`exit`, `quit`, `終了`）でループ終了
    - リセットコマンド（`reset`, `リセット`, `最初から`）で会話履歴・申請者情報リセット
    - `InvocationState(applicant_name=..., application_date=datetime.now().strftime("%Y-%m-%d"), session_id=...).model_dump()` で invocation_state を構築
    - 例外捕捉（詳細設計書に従う）:
      - `KeyboardInterrupt`: INFO ログ → break
      - `LoopLimitError`: WARNING ログ → continue
      - `ContextWindowOverflowException`: WARNING ログ → continue
      - `MaxTokensReachedException`: WARNING ログ → continue
      - `RuntimeError`: ERROR ログ（exc_info=True）→ continue
      - `Exception`: ERROR ログ（exc_info=True）→ continue
    - ログにはセッションIDを付加情報として含める
- **単体テスト内容**:
  - `_initialize()` が `Agent` インスタンスを生成すること（モック使用）
  - 終了コマンドでループが終了すること
  - リセットコマンドで会話履歴がリセットされること
  - 500文字超の入力でエラーメッセージが表示されること
  - `LoopLimitError` 発生時にループが継続すること（continue）
  - `KeyboardInterrupt` 発生時にループが終了すること（break）


---

## タスク12: 専門エージェント

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md`
  - `artifacts/03_system-design/outputs/マルチエージェント連携設計.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/12_skeleton_specialist_agent.md`
- **成果物のファイルパス**:
  - `artifacts/06_code-generation/src/agents/transport_agent.py`
  - `artifacts/06_code-generation/src/agents/expense_agent.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_specialist_agents.py`
- **実装内容**:
  - `transport_agent.py`（AG-003: 交通費精算申請エージェント）:
    - `_build_transport_agent(session_id, applicant_name, application_date, deadline)` ビルド関数:
      - `settings.transport` から設定取得
      - `get_transport_system_prompt(applicant_name, application_date, deadline_date=deadline, transport_policies=get_transport_policies(settings.transport.deadline_months, settings.transport.approval_threshold))` でプロンプト生成
      - `create_specialist_agent(session_id, system_prompt, tools=[calculate_transport_fare, generate_transport_report], agent_name="交通費精算申請エージェント", window_size=cfg.window_size, ...)` を返却
    - `@tool(context=True)` で `transport_agent(query, tool_context)` ツール関数:
      - `invoke_specialist_agent(query, tool_context, agent_id="AG-003", deadline_months=settings.transport.deadline_months, build_agent=_build_transport_agent)` を呼び出す
  - `expense_agent.py`（AG-002: 経費精算申請エージェント）:
    - `_build_expense_agent(session_id, applicant_name, application_date, deadline)` ビルド関数:
      - `settings.expense` から設定取得
      - `get_expense_system_prompt(applicant_name, application_date, deadline_date=deadline, expense_policies=get_expense_policies(...), expense_category_policies=get_expense_category_policies())` でプロンプト生成
      - `create_specialist_agent(session_id, system_prompt, tools=[generate_expense_report, image_reader], agent_name="経費精算申請エージェント", window_size=cfg.window_size, ...)` を返却
    - `@tool(context=True)` で `expense_agent(query, tool_context)` ツール関数:
      - `invoke_specialist_agent(query, tool_context, agent_id="AG-002", deadline_months=settings.expense.deadline_months, build_agent=_build_expense_agent)` を呼び出す
  - 例外捕捉（詳細設計書に従う）:
    - `LoopLimitError`: WARNING ログ → エラーメッセージ文字列を返す
    - `ContextWindowOverflowException`: WARNING ログ → エラーメッセージ文字列を返す
    - `MaxTokensReachedException`: WARNING ログ → エラーメッセージ文字列を返す
    - `RuntimeError`: ERROR ログ（exc_info=True）→ エラーメッセージ文字列を返す
    - `Exception`: ERROR ログ（exc_info=True）→ エラーメッセージ文字列を返す
  - ログにはクエリの先頭50文字を付加情報として含める
- **単体テスト内容**:
  - `_build_transport_agent()` が `Agent` インスタンスを返すこと（モック使用）
  - `_build_expense_agent()` が `Agent` インスタンスを返すこと（モック使用）
  - `transport_agent` ツール関数が文字列を返すこと（モック使用）
  - `expense_agent` ツール関数が文字列を返すこと（モック使用）
  - `LoopLimitError` 発生時にエラーメッセージ文字列が返ること

---

## タスク13: メインエントリーポイント

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`（起動フロー・申請者名取得）
  - `artifacts/03_system-design/outputs/ログ出力方式設計.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/13_skeleton_main.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/main.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_main.py`
- **実装内容**:
  - `load_dotenv()` で `.env` ファイルを読み込み
  - ログ設定（モジュールレベルで実行）:
    - `LOG_LEVEL` 環境変数から取得（デフォルト: `WARNING`）
    - `logs/` ディレクトリを `os.makedirs(exist_ok=True)` で作成
    - フォーマット: `"%(asctime)s [%(levelname)s] %(name)s - %(message)s"`
    - `RotatingFileHandler("logs/app.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")` INFO以上
    - `RotatingFileHandler("logs/error.log", maxBytes=10*1024*1024, backupCount=5, encoding="utf-8")` ERROR以上
    - `StreamHandler()` INFO以上
    - `logging.basicConfig(level=log_level, handlers=[console, app_handler, error_handler])`
    - `logging.getLogger("strands").setLevel(logging.WARNING)` でStrands過剰ログ抑制
  - `main()` 関数:
    - システム起動ログ出力
    - 申請者名の入力受付（アプリケーション起動時、対話ループ開始前）
    - `SessionManagerFactory.generate_session_id()` でセッションID生成
    - `OrchestratorAgent(applicant_name, session_id).run()` を実行
    - 正常終了ログ出力
    - 例外捕捉:
      - `KeyboardInterrupt`: `ErrorHandler.handle_keyboard_interrupt()` を print、INFO ログ
      - `Exception`: `ErrorHandler.handle_unexpected_error(e)` を print、ERROR ログ（exc_info=True）、`sys.exit(1)`
- **単体テスト内容**:
  - `main()` が `OrchestratorAgent.run()` を呼び出すこと（モック使用）
  - `KeyboardInterrupt` 発生時に `sys.exit` が呼ばれないこと
  - `Exception` 発生時に `sys.exit(1)` が呼ばれること

---

## タスク14: 資材配置（データファイル・テンプレート）

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/交通費計算ツール詳細設計.md`（データファイルパス定義）
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/14_design_data_files.md`
- **成果物のファイルパス**:
  - `artifacts/06_code-generation/src/data/train_routes.json`
  - `artifacts/06_code-generation/src/data/fixed_fares.json`
  - `artifacts/06_code-generation/src/template/交通費精算申請書テンプレート.xlsx`
  - `artifacts/06_code-generation/src/template/経費精算申請書テンプレート.xlsx`
- **単体テストコードのファイルパス**: なし（資材配置タスクのためテストなし）
- **実装内容**:
  - `materials/06_code-generation/train_fares.json` → `artifacts/06_code-generation/src/data/train_routes.json` にコピー
  - `materials/06_code-generation/fixed_fares.json` → `artifacts/06_code-generation/src/data/fixed_fares.json` にコピー
  - `materials/06_code-generation/交通費申請書_template.xlsx` → `artifacts/06_code-generation/src/template/交通費精算申請書テンプレート.xlsx` にコピー
  - `materials/06_code-generation/経費精算申請書_template.xlsx` → `artifacts/06_code-generation/src/template/経費精算申請書テンプレート.xlsx` にコピー
  - アプリケーション実行時は `src/data/` および `src/template/` 配下のファイルを参照する設計
- **単体テスト内容**: なし

---

## タスク15: エージェント動作パラメータ設定

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/03_system-design/outputs/システム基本情報.md`
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/15_skeleton_settings.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/config/settings.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_settings.py`
- **実装内容**:
  - `_AgentSettings(BaseSettings)` 基底クラス: `max_iterations=10`、`max_attempts=6`、`initial_delay=4`、`max_delay=240`
  - `OrchestratorSettings(_AgentSettings)`:
    - `window_size=30`、`max_turn_count=30`、`max_input_length=500`
    - `model_config = {"env_prefix": "ECAAS_ORCHESTRATOR_", "extra": "ignore"}`
  - `TransportSettings(_AgentSettings)`:
    - `window_size=20`、`deadline_months=3`、`approval_threshold=10000`
    - `model_config = {"env_prefix": "ECAAS_TRANSPORT_", "extra": "ignore"}`
  - `ExpenseSettings(_AgentSettings)`:
    - `window_size=15`、`deadline_months=3`、`approval_threshold=5000`
    - `model_config = {"env_prefix": "ECAAS_EXPENSE_", "extra": "ignore"}`
  - `_Settings` 集約クラス: `orchestrator = OrchestratorSettings()`、`transport = TransportSettings()`、`expense = ExpenseSettings()`
  - モジュールレベル変数 `settings = _Settings()` を定義
- **単体テスト内容**:
  - `settings.orchestrator.window_size` が 30 であること
  - `settings.transport.deadline_months` が 3 であること
  - `settings.expense.approval_threshold` が 5000 であること
  - 環境変数 `ECAAS_TRANSPORT_MAX_ITERATIONS=15` を設定した場合に上書きされること


---

## タスク16: ガードレール CloudFormation テンプレート

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ガードレール詳細設計.md`
  - `artifacts/03_system-design/outputs/ガードレール処理方式設計.md`
  - `artifacts/02_system-requirements/outputs/業務ルール定義.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/16_guardrails_cloudformation_yaml.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/guardrails/guardrails_cloudformation.yaml`
- **単体テストコードのファイルパス**: なし（YAMLファイルのためテストなし）
- **実装内容**:
  - `AWSTemplateFormatVersion: "2010-09-09"` を設定
  - `BedrockGuardrail` リソースを定義
  - `BlockedInputMessaging`・`BlockedOutputsMessaging` を詳細設計書のフォールバック応答に従い設定
  - `ContentPolicyConfig` に以下のフィルタを設定（詳細設計書のブロック条件に従う）:
    - `VIOLENCE`, `HATE`, `SEXUAL`, `INSULTS`, `MISCONDUCT`: InputStrength/OutputStrength HIGH、BLOCK
    - `PROMPT_ATTACK`: InputStrength HIGH、OutputStrength NONE（入力側のみ）
  - `SensitiveInformationPolicyConfig` に `CREDIT_DEBIT_CARD_CVV` を BLOCK で設定（詳細設計書の PII フィルター対象）
  - `WordPolicyConfig` に `PROFANITY` マネージドリストを設定
  - `CrossRegionConfig` に APAC ガードレールプロファイル ARN を設定
  - `Outputs` に `GuardrailId`・`GuardrailVersion` を出力
  - プレースホルダー `{xxx}` は詳細設計書の定義で置換すること
- **単体テスト内容**: なし

---

## タスク17: エージェント共通ユーティリティ

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/03_system-design/outputs/マルチエージェント連携設計.md`
  - `artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/ハンドラー詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/17_skeleton_base_agent.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/agents/base_agent.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_base_agent.py`
- **実装内容**:
  - `calculate_deadline(application_date, deadline_months)`:
    - `datetime.strptime(application_date, "%Y-%m-%d")` でパース
    - `relativedelta(months=deadline_months)` を加算
    - `strftime("%Y-%m-%d")` で返却
    - パース失敗時は `"要確認"` を返却
  - `create_specialist_agent(session_id, system_prompt, tools, agent_name, window_size, max_iterations, max_attempts, initial_delay, max_delay)`:
    - `SessionManagerFactory.create_session_manager(session_id)` でセッション管理を作成
    - `HumanApprovalHook(approval_callback=console_approval_callback)` を作成（コンソール承認コールバック）
    - `LoopControlHook(max_iterations=max_iterations, agent_name=agent_name)` を作成
    - `Agent(model=ModelConfig.get_model(), system_prompt=system_prompt, tools=tools, conversation_manager=SlidingWindowConversationManager(window_size=window_size, should_truncate_results=True, per_turn=False), callback_handler=None, retry_strategy=ModelRetryStrategy(max_attempts=max_attempts, initial_delay=initial_delay, max_delay=max_delay), hooks=[approval_hook, loop_hook], session_manager=session_manager)` を返却
  - `invoke_specialist_agent(query, tool_context, agent_id, deadline_months, build_agent)`:
    - `tool_context.invocation_state` から `applicant_name`・`application_date`・`session_id` を取得
    - INFO ログ出力（クエリ先頭50文字を含む）
    - `calculate_deadline(application_date, deadline_months)` で申請期限を計算
    - `build_agent(session_id, applicant_name, application_date, deadline)` でエージェントを生成
    - `child_invocation_state = {"applicant_name": ..., "application_date": ...}` を構築（session_id は除外）
    - `agent(query, invocation_state=child_invocation_state)` で呼び出し
    - 例外捕捉:
      - `LoopLimitError`: WARNING ログ → `ErrorHandler.handle_loop_limit_error(e)` を返す
      - `Exception`: ERROR ログ（exc_info=True）→ `ErrorHandler.handle_unexpected_error(e)` を返す
  - コンソール承認コールバック関数 `console_approval_callback(tool_name, tool_params)`:
    - ドラフト内容を表示し、`OK` / `修正` / `キャンセル` の3択をユーザーに提示
    - 戻り値: `tuple[bool, str]`（`(True, "")` / `(False, "CANCEL")` / `(False, "修正内容")`）
- **単体テスト内容**:
  - `calculate_deadline("2026-01-15", 3)` が `"2026-04-15"` を返すこと
  - `calculate_deadline("invalid", 3)` が `"要確認"` を返すこと
  - `create_specialist_agent()` が `Agent` インスタンスを返すこと（モック使用）
  - `invoke_specialist_agent()` が文字列を返すこと（モック使用）
  - `LoopLimitError` 発生時にエラーメッセージ文字列が返ること

---

## タスク18: ディレクトリ構造検証

- **ステータス**: [x] 完了
- **参照する規約**: `.kiro/steering/00_rule_directory_structure.md`
- **検証対象ディレクトリ**: `artifacts/06_code-generation/src/`
- **検証内容**:
  - R1準拠確認: `src/` 直下のディレクトリが許可リスト（`config/`, `interfaces/`, `models/`, `agents/`, `handlers/`, `tools/`, `prompt/`, `knowledge/`, `session/`, `storage/`, `data/`, `template/`, `sample/`, `output/`, `logs/`, `evals/`, `docs/`, `tests/`, `guardrails/`）のみであること
  - R2準拠確認: 各ファイルが正しいディレクトリに配置され、命名規則に従っていること
    - `*_agent.py` → `agents/`
    - `*_tools.py` または `*_generator.py` → `tools/`
    - `*_policies.py` → `knowledge/`
    - `prompt_*.py` → `prompt/`
    - `*_handler.py` または `*_hook.py` → `handlers/`
    - `*_manager.py` → `session/`
    - `*_config.py` または `*_settings.py` → `config/`
    - `data_models.py` → `models/`
    - `main.py` → プロジェクトルート（`src/`）
  - 全タスク（01〜17）の成果物ファイルが存在すること
- **違反時の報告形式**:
  - `⚠️ [違反種別]: [ファイルパス] → [修正方法]`
- **違反時の対応**: 検出された違反をすべて修正してからステータスを完了にすること

---

## タスク19: 結合テスト

- **ステータス**: [x] 完了
- **テスト対象**:
  - `models/data_models.py` ↔ `tools/transport_tools.py`（データモデルとツールの連携）
  - `models/data_models.py` ↔ `tools/output_generator.py`（データモデルとツールの連携）
  - `handlers/error_handler.py` ↔ `handlers/loop_control_hook.py`（LoopLimitError の発生と捕捉）
  - `handlers/human_approval_hook.py` ↔ `tools/output_generator.py`（承認フックとツール実行の連携）
  - `session/session_manager.py` ↔ `agents/orchestrator_agent.py`（セッション管理とエージェントの連携）
  - `agents/base_agent.py` ↔ `agents/transport_agent.py`（共通ユーティリティと専門エージェントの連携）
  - `agents/base_agent.py` ↔ `agents/expense_agent.py`（共通ユーティリティと専門エージェントの連携）
  - `knowledge/*_policies.py` ↔ `prompt/prompt_specialist_*.py`（ナレッジとプロンプト生成の連携）
  - `config/settings.py` ↔ `agents/base_agent.py`（設定値とエージェント生成の連携）
- **結合テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/integration/test_agent_integration.py`
- **結合テスト内容**:
  - `TransportCalculatorInput` でバリデーションした入力を `calculate_transport_fare` に渡して正常に計算できること
  - `ExpenseReportInput` でバリデーションした入力を `generate_expense_report` に渡して正常にファイル生成できること（モックテンプレート使用）
  - `LoopControlHook` が上限到達時に `LoopLimitError` を raise し、`ErrorHandler.handle_loop_limit_error()` が文字列を返すこと
  - `HumanApprovalHook` が承認コールバック `(True, "")` の場合にツールをキャンセルしないこと
  - `HumanApprovalHook` が承認コールバック `(False, "CANCEL")` の場合に `event.cancel_tool` が設定されること
  - `SessionManagerFactory.create_session_manager()` で生成したセッションマネージャーが `Agent` に渡せること（モック使用）
  - `calculate_deadline()` で計算した期限が `get_transport_system_prompt()` に正しく渡されること
  - `settings.transport.deadline_months` が `get_transport_policies()` の引数として正しく渡されること
