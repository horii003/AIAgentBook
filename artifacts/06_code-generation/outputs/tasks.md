# 実装タスク計画

## 共通参照規約
- `.kiro/steering/00_rule_directory_structure.md`
- `.kiro/steering/00_rule_project_conventions.md`
- `.kiro/steering/00_rule_code_review_checklist.md`

---

## タスク1: データモデル定義

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/データモデル詳細設計.md`
  - `artifacts/05_detailed-design/outputs/交通費計算ツール詳細設計.md`
  - `artifacts/05_detailed-design/outputs/申請書生成ツール詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/01_skeleton_data_models.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/models/data_models.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_data_models.py`
- **実装内容**:
  - 共通バリデーター関数 `validate_date_format` の定義（YYYY-MM-DD形式チェック）
  - 共通バリデーター関数 `normalize_transport_type` の定義（交通手段の表記正規化）
  - `InvocationState` モデルの定義（`user_name`, `request_date`, `session_id` フィールド）
  - マスタデータモデルの定義（`FixedFare`, `TrainFare` 等、`data/` 配下のJSONに対応）
  - ツール入力モデルの定義（`TransportCalculatorInput`, `GeneralExpenseInput` 等）
  - 出力生成モデルの定義（`TransportationExpenseOutput`, `GeneralExpenseOutput` 等）
  - `field_validator` による共通バリデーターの各モデルへの適用（ラムダラッパー禁止）
- **単体テスト内容**:
  - `validate_date_format`: 正常系（有効な日付文字列）、異常系（不正フォーマット）
  - `normalize_transport_type`: 各交通手段の正規化パターン
  - `InvocationState`: 必須フィールドの検証、バリデーションエラー
  - 各ツール入力モデル: 必須フィールド・任意フィールド・バリデーション
  - 各出力生成モデル: フィールド定義の確認

---

## タスク2: Bedrockモデル設定

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/03_system-design/outputs/共通設定方針.md`
  - `artifacts/03_system-design/outputs/システム基本情報.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/02_skeleton_model_config.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/config/model_config.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_model_config.py`
- **実装内容**:
  - `ModelConfig` クラスの定義
  - `DEFAULT_MODEL_ID` 定数の設定（`jp.anthropic.claude-sonnet-4-5-20250929-v1:0`）
  - `GUARDRAIL_ID`, `GUARDRAIL_VERSION` 定数の設定
  - `get_model()` クラスメソッドの実装（`@lru_cache(maxsize=1)` でキャッシュ）
  - `BedrockModel` インスタンスの生成（`guardrail_trace="enabled"` 含む）
- **単体テスト内容**:
  - `get_model()` が `BedrockModel` インスタンスを返すこと
  - `get_model()` が同一インスタンスを返すこと（キャッシュ確認）
  - モデルIDが正しく設定されていること

---

## タスク3: エージェント動作パラメータ設定

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/03_system-design/outputs/共通設定方針.md`
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/15_skeleton_settings.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/config/settings.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_settings.py`
- **実装内容**:
  - `_AgentSettings` 基底クラスの定義（`max_iterations`, `max_attempts`, `initial_delay`, `max_delay`）
  - `OrchestratorSettings` クラスの定義（`window_size=30`, `max_turn_count`, `max_input_length`, 環境変数プレフィックス設定）
  - `TransportationExpenseSettings` クラスの定義（`window_size=20`, `deadline_months`, 環境変数プレフィックス設定）
  - `GeneralExpenseSettings` クラスの定義（`window_size=20`, `deadline_months`, `approval_threshold`, 環境変数プレフィックス設定）
  - `_Settings` 集約クラスの定義（各エージェント設定インスタンスをフィールドとして保持）
  - モジュールレベル `settings` インスタンスの定義
- **単体テスト内容**:
  - 各設定クラスのデフォルト値確認
  - 環境変数による上書き確認
  - `settings.orchestrator`, `settings.transportation_expense`, `settings.general_expense` のアクセス確認

---

## タスク4: エラーハンドリング

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ErrorHandlerハンドラー詳細設計.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/03_skeleton_error_handler.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/handlers/error_handler.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_error_handler.py`
- **実装内容**:
  - `LoopLimitError` 例外クラスの定義（`current_iteration`, `max_iterations`, `agent_name` 属性、日本語メッセージ生成）
  - `ErrorHandler` クラスの定義（全メソッド `@staticmethod`、ログ出力なし）
  - `handle_keyboard_interrupt()` の実装（処理中断メッセージ）
  - `handle_loop_limit_error()` の実装（ループ上限到達メッセージ）
  - `handle_validation_error()` の実装（`error.errors()` 解析、日本語メッセージ生成）
  - `handle_runtime_error()` の実装
  - `handle_unexpected_error()` の実装（システム障害メッセージ）
  - ドメイン固有エラーハンドラの追加（詳細設計書に従う）
- **単体テスト内容**:
  - `LoopLimitError`: 属性値・メッセージ内容の確認
  - 各 `handle_*` メソッド: 戻り値が日本語文字列であること
  - `handle_validation_error`: Pydantic ValidationError を渡した場合のメッセージ確認
  - `ErrorHandler` がインスタンス化不要（staticmethod）であること

---

## タスク5: ReActループ制御フック

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/LoopControlHookハンドラー詳細設計.md`
  - `artifacts/03_system-design/outputs/実行制御方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/04_skeleton_loop_control_hook.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/handlers/loop_control_hook.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_loop_control_hook.py`
- **実装内容**:
  - `LoopControlHook(HookProvider)` クラスの定義
  - `__init__` の実装（`max_iterations`, `agent_name`, `current_iteration` 初期化）
  - `register_hooks` の実装（6イベントを `registry.add_callback()` で登録）
  - `on_before_invocation`: ループカウント初期化・ログ出力
  - `on_before_model_call`: 現在ループ回数のログ出力
  - `on_after_model_call`: カウントインクリメント・最大回数チェック・`LoopLimitError` 発生（`event.exception` 存在時はスキップ）
  - `_get_tool_name`: `event.tool_use` が None の場合は `"unknown"` を返すヘルパー
  - `on_before_tool_call`: ツール名ログ出力
  - `on_after_tool_call`: ツール完了ログ出力
  - `on_after_invocation`: 合計ループ回数ログ出力
- **単体テスト内容**:
  - `register_hooks` が6イベントを登録すること
  - `on_after_model_call` でカウントがインクリメントされること
  - 最大回数到達時に `LoopLimitError` が発生すること
  - `event.exception` 存在時にカウントがインクリメントされないこと
  - `_get_tool_name` が `None` の場合に `"unknown"` を返すこと

---

## タスク6: コンソール承認アダプター

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/HumanApprovalHookハンドラー詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/05_skeleton_human_approval_hook.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/handlers/console_approval_adapter.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_console_approval_adapter.py`
- **実装内容**:
  - `console_approval_callback(tool_name: str, tool_params: dict) -> tuple[bool, str]` 関数の定義
  - 申請内容の表示（`tool_name`, `tool_params` を整形して print）
  - ユーザー入力受付（承認 / 修正 / キャンセルの選択）
  - 戻り値: `(True, "")` = 承認、`(False, "CANCEL")` = キャンセル、`(False, "修正内容")` = 修正要望
- **単体テスト内容**:
  - 承認入力時に `(True, "")` を返すこと
  - キャンセル入力時に `(False, "CANCEL")` を返すこと
  - 修正要望入力時に `(False, "修正内容文字列")` を返すこと

---

## タスク7: Human-in-the-Loop承認フック

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/HumanApprovalHookハンドラー詳細設計.md`
  - `artifacts/03_system-design/outputs/実行制御方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/05_skeleton_human_approval_hook.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/handlers/human_approval_hook.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_human_approval_hook.py`
- **実装内容**:
  - `HumanApprovalHook(HookProvider)` クラスの定義
  - `APPROVAL_REQUIRED_TOOLS` クラス変数の設定（承認対象ツール名: `generate_transportation_expense_form`, `generate_general_expense_form`）
  - `__init__` の実装（`approval_callback`, `approval_required_tools` 引数）
  - `register_hooks` の実装（`BeforeToolCallEvent` を `registry.add_callback()` で登録）
  - `_on_before_tool_call` の実装（対象外ツールのスキップ・コールバック呼び出し・`event.cancel_tool` 設定）
  - `_build_cancel_message` の実装（キャンセル/修正要望に応じたLLM向けメッセージ生成）
- **単体テスト内容**:
  - 対象外ツール呼び出し時にコールバックが呼ばれないこと
  - 承認時に `event.cancel_tool` が設定されないこと
  - キャンセル時に `event.cancel_tool` にメッセージが設定されること
  - 修正要望時に `event.cancel_tool` に修正内容を含むメッセージが設定されること
  - `_build_cancel_message` のメッセージ内容確認



## タスク8: セッション管理

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/セッションマネージャ詳細設計.md`
  - `artifacts/03_system-design/outputs/セッション管理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/06_skeleton_session_manager.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/session/session_manager.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_session_manager.py`
- **実装内容**:
  - `SessionManagerFactory` クラスの定義
  - `generate_session_id(prefix: str = "") -> str` の実装（`YYYYMMDD_HHMMSS_uuid8` 形式）
  - `get_storage_dir() -> str` の実装（`_storage_dir` キャッシュ・`storage/sessions/` パス構築・自動作成）
  - `create_session_manager(session_id: str) -> FileSessionManager` の実装
  - `get_session_path(session_id: str) -> str` の実装
- **単体テスト内容**:
  - `generate_session_id()`: フォーマット確認（`YYYYMMDD_HHMMSS_uuid8`）
  - `generate_session_id("prefix")`: プレフィックス付きフォーマット確認
  - `get_storage_dir()`: 同一インスタンスを返すこと（キャッシュ確認）
  - `create_session_manager()`: `FileSessionManager` インスタンスを返すこと
  - `get_session_path()`: 正しいパスを返すこと

---

## タスク9: オーケストレーターシステムプロンプト

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/システムプロンプト詳細設計.md`
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/07_skeleton_prompt_orchestrator.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/prompt/prompt_orchestrator.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_prompt_orchestrator.py`
- **実装内容**:
  - `ORCHESTRATOR_SYSTEM_PROMPT` 定数の定義（静的プロンプト）
  - 役割定義（申請受付窓口エージェント AG-001）
  - 処理フロー（申請種別判断・専門エージェントへの振り分け）
  - 振り分け基準テーブル（交通費精算申請 → AG-002、経費精算申請 → AG-003）
  - エラーハンドリング指示・対話ルール
- **単体テスト内容**:
  - `ORCHESTRATOR_SYSTEM_PROMPT` が空でない文字列であること
  - 振り分け先エージェント名（`transportation_expense_agent`, `general_expense_agent`）が含まれること

---

## タスク10: 交通費精算申請エージェントシステムプロンプト

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/システムプロンプト詳細設計.md`
  - `artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/ナレッジ・業務ルール詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/08_skeleton_prompt_specialist.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/prompt/prompt_transportation_expense.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_prompt_transportation_expense.py`
- **実装内容**:
  - `_TRANSPORTATION_EXPENSE_SYSTEM_PROMPT_TEMPLATE` テンプレート定数の定義
  - `get_transportation_expense_system_prompt(applicant_name, application_date, deadline, transportation_policies) -> str` 関数の定義（動的生成）
  - テンプレートプレースホルダーと引数の一対一対応（未使用引数・未定義プレースホルダー禁止）
  - 役割定義・処理フロー・業務ルール・エラーハンドリング指示を含むプロンプト
- **単体テスト内容**:
  - `get_transportation_expense_system_prompt()` が文字列を返すこと
  - 引数の値がプロンプトに反映されること（`applicant_name`, `application_date`, `deadline`）
  - `transportation_policies` の内容が含まれること

---

## タスク11: 経費精算申請エージェントシステムプロンプト

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/システムプロンプト詳細設計.md`
  - `artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/ナレッジ・業務ルール詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/08_skeleton_prompt_specialist.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/prompt/prompt_general_expense.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_prompt_general_expense.py`
- **実装内容**:
  - `_GENERAL_EXPENSE_SYSTEM_PROMPT_TEMPLATE` テンプレート定数の定義
  - `get_general_expense_system_prompt(applicant_name, application_date, deadline, receipt_policies) -> str` 関数の定義（動的生成）
  - テンプレートプレースホルダーと引数の一対一対応
  - 役割定義・処理フロー（領収書画像解析含む）・業務ルール・エラーハンドリング指示を含むプロンプト
- **単体テスト内容**:
  - `get_general_expense_system_prompt()` が文字列を返すこと
  - 引数の値がプロンプトに反映されること
  - `receipt_policies` の内容が含まれること

---

## タスク12: 交通費精算ポリシー

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ナレッジ・業務ルール詳細設計.md`
  - `artifacts/02_system-requirements/outputs/業務ルール定義.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/09_skeleton_policies.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/knowledge/transportation_policies.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_transportation_policies.py`
- **実装内容**:
  - `get_transportation_policies(deadline_months: int, approval_threshold: int) -> str` 関数の定義
  - 交通費精算申請の業務ルール（申請期限・上長承認閾値等）をマークダウン形式で返却
  - ビジネスルール値は引数で受け取り動的展開（ハードコード禁止）
  - 他モジュールへの依存なし（純粋なテキスト返却）
- **単体テスト内容**:
  - `get_transportation_policies()` が文字列を返すこと
  - `deadline_months` の値がルールテキストに反映されること
  - `approval_threshold` の値がルールテキストに反映されること

---

## タスク13: 経費精算ポリシー

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ナレッジ・業務ルール詳細設計.md`
  - `artifacts/02_system-requirements/outputs/業務ルール定義.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/09_skeleton_policies.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/knowledge/receipt_policies.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_receipt_policies.py`
- **実装内容**:
  - `get_receipt_policies(deadline_months: int, approval_threshold: int) -> str` 関数の定義
  - 経費精算申請の業務ルール（申請期限・上長承認閾値・経費区分等）をマークダウン形式で返却
  - ビジネスルール値は引数で受け取り動的展開（ハードコード禁止）
  - 他モジュールへの依存なし（純粋なテキスト返却）
- **単体テスト内容**:
  - `get_receipt_policies()` が文字列を返すこと
  - `deadline_months` の値がルールテキストに反映されること
  - `approval_threshold` の値がルールテキストに反映されること



## タスク14: 交通費計算ツール

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/交通費計算ツール詳細設計.md`
  - `artifacts/05_detailed-design/outputs/データモデル詳細設計.md`
  - `artifacts/03_system-design/outputs/バリデーション方針.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/10_skeleton_tools.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/tools/transport_calculator.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_transport_calculator.py`
- **実装内容**:
  - `_load_fixed_fares()` / `_load_train_fares()` データ読み込み関数の定義（`_loaded` フラグによるキャッシュ管理）
  - `@tool` デコレータによる `calculate_transport_fare(departure, destination, transport_type, travel_date, purpose) -> dict` の定義
  - `TransportCalculatorInput` Pydanticモデルによる入力バリデーション
  - 電車: `train_fares.json` 検索による運賃返却
  - バス・タクシー・飛行機: `fixed_fares.json` 参照による運賃返却
  - エラー返却辞書のキー名を出力Pydanticモデルのフィールド名と一致させる
  - `ValidationError` → `Exception` の順でキャッチ（複数 `except` 節の統合）
- **単体テスト内容**:
  - 電車運賃の正常計算（`train_fares.json` モック）
  - 固定運賃の正常取得（`fixed_fares.json` モック）
  - 存在しない経路のエラー返却
  - 入力バリデーションエラー時の返却
  - `_loaded` フラグによるキャッシュ動作確認（空データでも再ロードしないこと）

---

## タスク15: 申請書生成ツール

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/申請書生成ツール詳細設計.md`
  - `artifacts/05_detailed-design/outputs/データモデル詳細設計.md`
  - `artifacts/03_system-design/outputs/バリデーション方針.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/10_skeleton_tools.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/tools/output_generator.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_output_generator.py`
- **実装内容**:
  - `@tool(context=True)` デコレータによる `generate_transportation_expense_form(transport_records: list, tool_context: ToolContext) -> dict` の定義
  - `@tool(context=True)` デコレータによる `generate_general_expense_form(expense_records: list, tool_context: ToolContext) -> dict` の定義
  - `tool_context.invocation_state` から `user_name`, `request_date` を取得
  - `InvocationState` による `invocation_state` の再バリデーション
  - 共通ヘルパー `_generate_form(template_path, validated, write_rows_fn, output_filename) -> dict` の定義（DRY原則）
  - テンプレートファイル存在確認・openpyxlによるExcel書き込み・`output/` への保存
  - 上長承認要否フラグが True の場合の承認欄追加
  - エラー返却辞書のキー名を出力Pydanticモデルのフィールド名と一致させる
- **単体テスト内容**:
  - 交通費申請書の正常生成（テンプレートモック）
  - 経費申請書の正常生成（テンプレートモック）
  - テンプレートファイル不在時のエラー返却
  - `invocation_state` バリデーションエラー時の返却
  - 上長承認欄の追加確認
  - `_generate_form` ヘルパーの共通処理確認

---

## タスク16: 静的データファイルの配置

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/交通費計算ツール詳細設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/14_design_data_files.md`
- **成果物のファイルパス**:
  - `artifacts/06_code-generation/src/data/fixed_fares.json`（コピー元: `materials/06_code-generation/fixed_fares.json`）
  - `artifacts/06_code-generation/src/data/train_fares.json`（コピー元: `materials/06_code-generation/train_fares.json`）
  - `artifacts/06_code-generation/src/template/交通費精算申請書テンプレート.xlsx`（コピー元: `materials/06_code-generation/交通費申請書_template.xlsx`）
  - `artifacts/06_code-generation/src/template/経費精算申請書テンプレート.xlsx`（コピー元: `materials/06_code-generation/経費精算申請書_template.xlsx`）
- **単体テストコードのファイルパス**: なし（ファイル配置タスクのため）
- **実装内容**:
  - `materials/06_code-generation/fixed_fares.json` → `artifacts/06_code-generation/src/data/fixed_fares.json` へコピー
  - `materials/06_code-generation/train_fares.json` → `artifacts/06_code-generation/src/data/train_fares.json` へコピー
  - `materials/06_code-generation/交通費申請書_template.xlsx` → `artifacts/06_code-generation/src/template/交通費精算申請書テンプレート.xlsx` へコピー
  - `materials/06_code-generation/経費精算申請書_template.xlsx` → `artifacts/06_code-generation/src/template/経費精算申請書テンプレート.xlsx` へコピー
- **単体テスト内容**:
  - 各ファイルが正しいパスに存在すること

---

## タスク17: エージェント共通ユーティリティ

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md`
  - `artifacts/03_system-design/outputs/マルチエージェント連携設計.md`
  - `artifacts/03_system-design/outputs/セッション管理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/17_skeleton_base_agent.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/agents/base_agent.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_base_agent.py`
- **実装内容**:
  - `calculate_deadline(application_date: str, deadline_months: int) -> str` の実装（`dateutil.relativedelta` 使用、パース失敗時は `"要確認"` 返却）
  - `create_specialist_agent(session_id, system_prompt, tools, agent_name, window_size, max_iterations, max_attempts, initial_delay, max_delay) -> Agent` の実装
    - `SessionManagerFactory.create_session_manager()` でセッション管理作成
    - `HumanApprovalHook(approval_callback=console_approval_callback)` 作成
    - `LoopControlHook(max_iterations, agent_name)` 作成
    - `Agent()` インスタンス生成・返却（R9.5準拠）
  - `invoke_specialist_agent(query, tool_context, agent_id, deadline_months, build_agent) -> str` の実装
    - `invocation_state` から `applicant_name`, `application_date`, `session_id` 取得
    - `calculate_deadline()` で申請期限計算
    - `build_agent()` でエージェント生成
    - `child_invocation_state` 構築（`session_id` 除外）
    - `LoopLimitError` → `Exception` の順でキャッチ・`ErrorHandler` 委譲
- **単体テスト内容**:
  - `calculate_deadline()`: 正常計算・パース失敗時の `"要確認"` 返却
  - `create_specialist_agent()`: `Agent` インスタンスを返すこと
  - `invoke_specialist_agent()`: `LoopLimitError` 発生時のエラーメッセージ返却
  - `invoke_specialist_agent()`: `Exception` 発生時のエラーメッセージ返却

---

## タスク18: オーケストレーターエージェント

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/データモデル詳細設計.md`
  - `artifacts/03_system-design/outputs/マルチエージェント連携設計.md`
  - `artifacts/03_system-design/outputs/セッション管理方針.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/11_skeleton_orchestrator_agent.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/agents/orchestrator_agent.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_orchestrator_agent.py`
- **実装内容**:
  - `OrchestratorAgent` クラスの定義
  - `__init__`: `_session_id`, `_session_manager`, `agent`, `_user_name` 等のインスタンス変数初期化
  - `_initialize()`: ユーザー名収集・セッションID生成・`SessionManagerFactory` 呼び出し・`LoopControlHook` 作成・`Agent()` インスタンス生成（`window_size=30`, `hooks=[loop_control_hook]`）
  - `run()`: 対話ループ（ユーザー入力受付・終了条件判定・`InvocationState` 構築・`model_dump()` 渡し・エージェント呼び出し・応答表示）
  - `LoopLimitError` → `Exception` の順でキャッチ・`ErrorHandler` 委譲
- **単体テスト内容**:
  - `_initialize()` が `Agent` インスタンスを生成すること
  - `run()` の終了条件判定（終了キーワード入力時）
  - `InvocationState` が正しく構築されること
  - エラーハンドリングの確認

---

## タスク19: 交通費精算申請エージェント

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/データモデル詳細設計.md`
  - `artifacts/03_system-design/outputs/マルチエージェント連携設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/12_skeleton_specialist_agent.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/agents/transportation_expense_agent.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_transportation_expense_agent.py`
- **実装内容**:
  - `_build_transportation_expense_agent(session_id, applicant_name, application_date, deadline) -> Agent` ビルド関数の定義
    - `settings.transportation_expense` から設定取得
    - `get_transportation_expense_system_prompt()` でプロンプト生成（`get_transportation_policies()` に `settings` から値を渡す）
    - `create_specialist_agent()` でエージェント生成（`tools=[calculate_transport_fare, generate_transportation_expense_form]`）
  - `@tool(context=True)` による `transportation_expense_agent(query: str, tool_context: ToolContext) -> str` ツール関数の定義
    - `invoke_specialist_agent()` 呼び出し（`agent_id="AG-002"`, `deadline_months=settings.transportation_expense.deadline_months`）
- **単体テスト内容**:
  - `_build_transportation_expense_agent()` が `Agent` インスタンスを返すこと
  - `transportation_expense_agent()` ツール関数が文字列を返すこと
  - `LoopLimitError` 発生時のエラーメッセージ返却

---

## タスク20: 経費精算申請エージェント

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md`
  - `artifacts/05_detailed-design/outputs/データモデル詳細設計.md`
  - `artifacts/03_system-design/outputs/マルチエージェント連携設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/12_skeleton_specialist_agent.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/agents/general_expense_agent.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_general_expense_agent.py`
- **実装内容**:
  - `_build_general_expense_agent(session_id, applicant_name, application_date, deadline) -> Agent` ビルド関数の定義
    - `settings.general_expense` から設定取得
    - `get_general_expense_system_prompt()` でプロンプト生成（`get_receipt_policies()` に `settings` から値を渡す）
    - `create_specialist_agent()` でエージェント生成（`tools=[generate_general_expense_form]`、`strands_tools.image_reader` 含む）
  - `@tool(context=True)` による `general_expense_agent(query: str, tool_context: ToolContext) -> str` ツール関数の定義
    - `invoke_specialist_agent()` 呼び出し（`agent_id="AG-003"`, `deadline_months=settings.general_expense.deadline_months`）
- **単体テスト内容**:
  - `_build_general_expense_agent()` が `Agent` インスタンスを返すこと
  - `general_expense_agent()` ツール関数が文字列を返すこと
  - `LoopLimitError` 発生時のエラーメッセージ返却

---

## タスク21: メインエントリーポイント

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md`
  - `artifacts/03_system-design/outputs/共通設定方針.md`
  - `artifacts/03_system-design/outputs/例外処理方針.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/13_skeleton_main.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/main.py`
- **単体テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/unit/test_main.py`
- **実装内容**:
  - `.env` ファイルの読み込み（`load_dotenv()`）
  - ログ設定（`LOG_LEVEL` 環境変数取得・`logs/` ディレクトリ作成・3ハンドラー構成: console/app.log/error.log）
  - `RotatingFileHandler` 設定（10MB × 5世代、UTF-8エンコーディング）
  - `logging.getLogger("strands").setLevel(logging.WARNING)` によるStrands SDKログ抑制
  - `main()` 関数の定義（`OrchestratorAgent` 生成・`run()` 呼び出し）
  - `KeyboardInterrupt` → `Exception` の順でキャッチ・`ErrorHandler` 委譲
- **単体テスト内容**:
  - `main()` が正常終了すること（`OrchestratorAgent.run()` モック）
  - `KeyboardInterrupt` 発生時の処理確認
  - `Exception` 発生時の `sys.exit(1)` 確認

---

## タスク22: ガードレール CloudFormation テンプレート

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/05_detailed-design/outputs/ガードレール詳細設計.md`
  - `artifacts/02_system-requirements/outputs/ガードレール要件定義.md`
  - `artifacts/03_system-design/outputs/ガードレール処理方式設計.md`
- **参照するスケルトンコード**: `.kiro/artifact-workflow/templates/06_code-generation/16_guardrails_cloudformation_yaml.md`
- **成果物のファイルパス**: `artifacts/06_code-generation/src/guardrails/guardrails_cloudformation.yaml`
- **単体テストコードのファイルパス**: なし（YAMLテンプレートのため）
- **実装内容**:
  - `BedrockGuardrail` CloudFormation リソースの定義
  - `BlockedInputMessaging` / `BlockedOutputsMessaging` の設定（詳細設計書のフォールバック応答）
  - `ContentPolicyConfig`: 詳細設計書のブロック条件に従いフィルタ列挙（`PROMPT_ATTACK` は入力側のみ）
  - `WordPolicyConfig`: `PROFANITY` マネージドリスト設定
  - `SensitiveInformationPolicyConfig`: 詳細設計書の対象PII種別を列挙
  - `CrossRegionConfig`: APACガードレールプロファイル設定
  - `Outputs`: `GuardrailId`, `GuardrailVersion` のエクスポート
- **単体テスト内容**:
  - YAMLとして正しくパースできること
  - 必須プロパティ（`BlockedInputMessaging`, `ContentPolicyConfig` 等）が存在すること

---

## タスク23: プロジェクト設定ファイル群

- **ステータス**: [x] 完了
- **参照する設計書**:
  - `artifacts/03_system-design/outputs/共通設定方針.md`
  - `artifacts/03_system-design/outputs/システム基本情報.md`
- **参照するスケルトンコード**: なし（プロジェクト設定ファイル）
- **成果物のファイルパス**:
  - `artifacts/06_code-generation/src/pyproject.toml`
  - `artifacts/06_code-generation/src/.env.template`
  - `artifacts/06_code-generation/src/.gitignore`
  - `artifacts/06_code-generation/src/README.md`
  - `artifacts/06_code-generation/src/config/__init__.py`
  - `artifacts/06_code-generation/src/models/__init__.py`
  - `artifacts/06_code-generation/src/agents/__init__.py`
  - `artifacts/06_code-generation/src/handlers/__init__.py`
  - `artifacts/06_code-generation/src/tools/__init__.py`
  - `artifacts/06_code-generation/src/prompt/__init__.py`
  - `artifacts/06_code-generation/src/knowledge/__init__.py`
  - `artifacts/06_code-generation/src/session/__init__.py`
  - `artifacts/06_code-generation/src/tests/__init__.py`
  - `artifacts/06_code-generation/src/tests/unit/__init__.py`
  - `artifacts/06_code-generation/src/tests/integration/__init__.py`
- **単体テストコードのファイルパス**: なし
- **実装内容**:
  - `pyproject.toml`: 依存パッケージ定義（R6の技術スタック準拠、バージョン固定）、pytest設定
  - `.env.template`: 必須環境変数一覧（`LOG_LEVEL`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `GUARDRAIL_ID`, `GUARDRAIL_VERSION`）
  - `.gitignore`: `.env`, `__pycache__/`, `*.pyc`, `storage/`, `logs/`, `output/` 等を除外
  - `README.md`: プロジェクト概要・セットアップ手順・実行方法
  - 各ディレクトリの `__init__.py`: 空ファイル
- **単体テスト内容**:
  - なし

---

## タスク24: ディレクトリ構造検証

- **ステータス**: [x] 完了
- **参照する規約**: `.kiro/steering/00_rule_directory_structure.md`
- **検証対象ディレクトリ**: `artifacts/06_code-generation/src/`
- **検証内容**:
  - R1準拠確認: `src/` 直下のディレクトリが許可リスト（`config/`, `models/`, `agents/`, `handlers/`, `tools/`, `prompt/`, `knowledge/`, `session/`, `storage/`, `data/`, `template/`, `sample/`, `output/`, `logs/`, `guardrails/`, `evals/`, `docs/`, `tests/`）のみであること
  - R2準拠確認: 各ファイルが正しいディレクトリに配置され、命名規則に従っていること（例: `*_agent.py` → `agents/`、`*_tools.py` または `*_generator.py` → `tools/`、`*_policies.py` → `knowledge/`、`prompt_*.py` → `prompt/`）
- **違反時の報告形式**:
  - `⚠️ [違反種別]: [ファイルパス] → [修正方法]`
- **違反時の対応**: 検出された違反をすべて修正してからステータスを完了にすること

---

## タスク25: 結合テスト

- **ステータス**: [x] 完了
- **テスト対象**:
  - オーケストレーター → 交通費精算申請エージェント → 交通費計算ツール → 申請書生成ツール の連携
  - オーケストレーター → 経費精算申請エージェント → 申請書生成ツール の連携
  - `InvocationState` の伝播（オーケストレーター → 専門エージェント → ツール）
  - `HumanApprovalHook` による承認フロー（承認・キャンセル・修正要望）
  - `LoopControlHook` によるループ制御（最大回数到達時の `LoopLimitError`）
  - セッション永続化（`FileSessionManager` による会話履歴の保存・復元）
- **結合テストコードのファイルパス**: `artifacts/06_code-generation/src/tests/integration/test_agent_integration.py`
- **結合テスト内容**:
  - 交通費精算申請の正常フロー（移動情報収集 → 運賃計算 → 申請書生成）
  - 経費精算申請の正常フロー（経費情報収集 → 申請書生成）
  - `invocation_state` が各ツールに正しく伝播されること
  - 承認フックのキャンセル時に申請が中止されること
  - 承認フックの修正要望時にエージェントが再生成を試みること
  - ループ上限到達時に `LoopLimitError` が発生し適切なメッセージが返ること
  - セッションIDが同一の場合に会話履歴が復元されること

