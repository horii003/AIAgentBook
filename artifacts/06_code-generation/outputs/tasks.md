# 実装タスク計画

## 共通参照元

- `.kiro/steering/00_rule_directory_structure.md`
- `.kiro/steering/00_rule_project_conventions.md`

---

## タスク01: 資材配置

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/04_basic-design/outputs/データモデル基本設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/14_design_data_files.md
- **成果物のファイルパス**:
  - artifacts/06_code-generation/src/data/fixed_fares.json
  - artifacts/06_code-generation/src/data/train_fares.json
  - artifacts/06_code-generation/src/template/交通費精算申請書テンプレート.xlsx
  - artifacts/06_code-generation/src/template/経費精算申請書テンプレート.xlsx
- **単体テストコードのファイルパス**: なし
- **実装内容**:
  - materials/06_code-generation/fixed_fares.json → artifacts/06_code-generation/src/data/fixed_fares.json へコピー
  - materials/06_code-generation/train_fares.json → artifacts/06_code-generation/src/data/train_fares.json へコピー
  - materials/06_code-generation/交通費申請書_template.xlsx → artifacts/06_code-generation/src/template/交通費精算申請書テンプレート.xlsx へコピー
  - materials/06_code-generation/経費精算申請書_template.xlsx → artifacts/06_code-generation/src/template/経費精算申請書テンプレート.xlsx へコピー
  - 必要なディレクトリ（data/, template/）の作成
- **単体テスト内容**:
  - なし（静的ファイル配置のため）

---

## タスク02: データモデル定義（data_models.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/データモデル詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/01_skeleton_data_models.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/models/data_models.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_data_models.py
- **実装内容**:
  - 共通バリデーター関数の定義（validate_station_name, normalize_transport_type, validate_date_format）
  - InvocationState エージェント状態モデルの定義
  - TrainRouteRecord マスタデータモデルの定義
  - TransportCalculatorInput / TransportCalculatorOutput ツール入出力モデルの定義
  - ExpenseReportInput / ExpenseItem / TransportReportInput / TransportItem 出力生成モデルの定義
  - ReportOutput 出力結果モデルの定義
  - field_validator による共通バリデーション適用
- **単体テスト内容**:
  - 正常系: 有効データでモデル生成、交通手段/駅名の正規化確認
  - 異常系: 空文字、不正交通手段、負の金額、不正日付、空リストでValidationError
  - 境界値: 金額0(ge=0許容)、金額-1(拒否)、運賃1(gt=0許容)、運賃0(拒否)
  - シリアライズ: model_dump()で正規化済み値が返される確認

---

## タスク03: モデル設定（model_config.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/03_system-design/outputs/共通設定方針.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/02_skeleton_model_config.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/config/model_config.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_model_config.py
- **実装内容**:
  - ModelConfig クラスの定義
  - DEFAULT_MODEL_ID 定数（jp.anthropic.claude-sonnet-4-5-20250929-v1:0）
  - GUARDRAIL_ID / GUARDRAIL_VERSION の環境変数参照
  - @classmethod @lru_cache(maxsize=1) による get_model() メソッド
  - BedrockModel インスタンス生成（guardrail_trace="enabled"）
- **単体テスト内容**:
  - get_model() が BedrockModel インスタンスを返すこと
  - lru_cache により同一インスタンスが返されること
  - 環境変数からガードレールID/バージョンが正しく読み込まれること

---

## タスク04: 設定管理（settings.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/03_system-design/outputs/共通設定方針.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/15_skeleton_settings.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/config/settings.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_settings.py
- **実装内容**:
  - _AgentSettings 基底クラス（max_iterations, max_attempts, initial_delay, max_delay）
  - OrchestratorSettings クラス（window_size=30）
  - TransportSettings クラス（window_size, deadline_months, approval_threshold）
  - ExpenseSettings クラス（window_size, deadline_months, approval_threshold）
  - _Settings 集約クラスと settings モジュールレベル変数
  - pydantic-settings による環境変数オーバーライド対応
- **単体テスト内容**:
  - デフォルト値が正しく設定されること
  - 環境変数によるオーバーライドが機能すること
  - settings モジュール変数からアクセスできること


---

## タスク05: エラーハンドラー（error_handler.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/ハンドラー詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/03_skeleton_error_handler.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/handlers/error_handler.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_error_handler.py
- **実装内容**:
  - LoopLimitError カスタム例外クラスの定義（current_iteration, max_iterations, agent_name）
  - ErrorHandler クラス（全メソッド @staticmethod）
  - handle_keyboard_interrupt() — 中断メッセージ返却
  - handle_loop_limit_error() — ループ上限到達メッセージ返却
  - handle_validation_error() — バリデーションエラーメッセージ返却
  - handle_runtime_error() — ランタイムエラーメッセージ返却
  - handle_unexpected_error() — 予期しないエラーメッセージ返却
  - handle_throttling_error() — スロットリングエラーメッセージ返却
  - handle_max_tokens_error() — トークン上限エラーメッセージ返却
  - handle_context_window_error() — コンテキストウィンドウエラーメッセージ返却
  - handle_fare_data_error() — 運賃データエラーメッセージ返却
  - handle_calculation_error() — 計算エラーメッセージ返却
  - handle_file_save_error() — ファイル保存エラーメッセージ返却
- **単体テスト内容**:
  - 各handleメソッドが適切なメッセージ文字列を返すこと
  - 空/None入力で例外が発生しないこと
  - LoopLimitError が正しい属性を保持すること

---

## タスク06: ループ制御フック（loop_control_hook.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/ハンドラー詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/04_skeleton_loop_control_hook.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/handlers/loop_control_hook.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_loop_control_hook.py
- **実装内容**:
  - LoopControlHook(HookProvider) クラスの定義
  - register_hooks() で6イベント登録（registry.add_callback使用）
  - _handle_before_invocation() — ループカウント初期化
  - _handle_before_model_call() — ループカウントインクリメント・上限チェック
  - _handle_after_model_call() — モデル呼び出し後ログ
  - _handle_before_tool_call() — ツール実行前ログ
  - _handle_after_tool_call() — ツール実行後ログ
  - _handle_after_invocation() — エージェント呼び出し完了ログ
  - _get_tool_name() ヘルパーメソッド（R9.8.6準拠）
  - 最大回数到達時に LoopLimitError を発生
- **単体テスト内容**:
  - 9回のモデル呼び出しで正常動作すること
  - 10回目でLoopLimitErrorが発生すること
  - BeforeInvocationでカウントがリセットされること
  - event.exceptionが設定されている場合にスキップすること

---

## タスク07: ガードレール定義（guardrails_cloudformation.yaml）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/ガードレール詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/16_guardrails_cloudformation_yaml.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/guardrails/guardrails_cloudformation.yaml
- **単体テストコードのファイルパス**: なし
- **実装内容**:
  - AWS::Bedrock::Guardrail リソース定義
  - ContentPolicyConfig（VIOLENCE, HATE, SEXUAL, INSULTS, MISCONDUCT, PROMPT_ATTACK）
  - WordPolicyConfig（PROFANITY + カスタム単語）
  - SensitiveInformationPolicyConfig（PII種別のBLOCK/ANONYMIZE）
  - CrossRegionConfig 設定
  - Outputs（GuardrailId, GuardrailVersion）
- **単体テスト内容**:
  - なし（CloudFormation定義ファイルのため）

---

## タスク08: Human-in-the-Loop承認フック（human_approval_hook.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/ハンドラー詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/05_skeleton_human_approval_hook.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/handlers/human_approval_hook.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_human_approval_hook.py
- **実装内容**:
  - HumanApprovalHook(HookProvider) クラスの定義
  - register_hooks() で BeforeToolCallEvent のみ登録
  - APPROVAL_REQUIRED_TOOLS で承認対象ツールをフィルタリング
  - approval_callback（外部注入）によるUI分離アーキテクチャ
  - _handle_before_tool_call() — 承認ゲート処理
  - event.cancel_tool によるツール実行キャンセル
  - _build_cancel_message() でLLMへの修正指示メッセージ生成
- **単体テスト内容**:
  - 対象ツールで承認ゲートが発火すること
  - 承認OK時にツールが実行されること
  - 修正指示時にevent.cancel_toolにメッセージが設定されること
  - キャンセル時にevent.cancel_toolにキャンセルメッセージが設定されること
  - 対象外ツールではスキップされること

---

## タスク09: セッションマネージャ（session_manager.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/セッションマネージャ詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/06_skeleton_session_manager.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/session/session_manager.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_session_manager.py
- **実装内容**:
  - SessionManagerFactory クラス（全メソッド @staticmethod）
  - generate_session_id() — タイムスタンプ+UUID8文字形式のID生成
  - create_session_manager(session_id) — FileSessionManager インスタンス生成
  - session_exists(session_id) — セッション存在確認
  - get_session_dir(session_id) — セッションディレクトリパス取得
  - storage/sessions/ ディレクトリの自動作成
- **単体テスト内容**:
  - セッションID形式が {YYYYMMDDHHMMSS}_{UUID8文字} であること
  - FileSessionManager が正しく生成されること
  - ディレクトリが自動作成されること
  - session_exists() が正しく判定すること
  - 100回連続生成で全て一意であること

---

## タスク10: オーケストレータープロンプト（prompt_orchestrator.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/システムプロンプト詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/07_skeleton_prompt_orchestrator.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/prompt/prompt_orchestrator.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_prompt_orchestrator.py
- **実装内容**:
  - ORCHESTRATOR_SYSTEM_PROMPT 定数の定義
  - 役割定義（受付窓口エージェント）
  - 処理フロー（依頼受付→分析→振り分け→完了確認）
  - 振り分け基準テーブル（交通費精算→transport_agent、経費精算→expense_agent）
  - エラーハンドリング指示・対話ルール
- **単体テスト内容**:
  - ORCHESTRATOR_SYSTEM_PROMPT が非空文字列であること
  - 振り分け基準キーワードがプロンプトに含まれること
  - エージェント名がプロンプトに含まれること

---

## タスク11: 専門エージェントプロンプト（prompt_transport.py / prompt_expense.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/システムプロンプト詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/08_skeleton_prompt_specialist.md
- **成果物のファイルパス**:
  - artifacts/06_code-generation/src/prompt/prompt_transport.py
  - artifacts/06_code-generation/src/prompt/prompt_expense.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_prompt_specialist.py
- **実装内容**:
  - get_transport_system_prompt(applicant_name, application_date, deadline_date) 動的生成関数
  - get_expense_system_prompt(applicant_name, application_date, deadline_date) 動的生成関数
  - knowledge/ からビジネスルールを引数で受け取り埋め込み
  - テンプレートプレースホルダーと引数の一対一対応（R9.12.2準拠）
  - 役割定義・処理フロー・重要な注意事項・対話ルール
- **単体テスト内容**:
  - applicant_name/application_date/deadline_date が正しく埋め込まれること
  - 返却値が非空文字列であること
  - ビジネスルールテキストがプロンプトに含まれること

---

## タスク12: ナレッジ・業務ルール（knowledge/）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/ナレッジ・業務ルール詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/09_skeleton_policies.md
- **成果物のファイルパス**:
  - artifacts/06_code-generation/src/knowledge/__init__.py
  - artifacts/06_code-generation/src/knowledge/application_policies.py
  - artifacts/06_code-generation/src/knowledge/transport_policies.py
  - artifacts/06_code-generation/src/knowledge/expense_policies.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_knowledge.py
- **実装内容**:
  - get_application_policies() — 申請種別判断ルール・申請先情報
  - get_transport_policies(deadline_months, approval_threshold) — 交通費精算業務ルール
  - get_expense_policies(deadline_months, approval_threshold) — 経費精算業務ルール
  - get_expense_category_policies() — 経費区分判断基準
  - ビジネスルール値は明示的な名前付き引数で受け取り（R9.12.3準拠）
  - 他モジュールへの依存なし（純粋なテキスト返却）
- **単体テスト内容**:
  - 各関数が非空文字列を返すこと
  - 設定値（deadline_months, approval_threshold）が正しく展開されること
  - BRL-01〜BRL-17の各ルールキーワードが含まれること

---

## タスク13: 交通費計算ツール（transport_tools.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/交通費計算ツール詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/10_skeleton_tools.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/tools/transport_tools.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_transport_tools.py
- **実装内容**:
  - _load_train_routes() — 電車経路データ読み込み（キャッシュ付き、初期化フラグ管理）
  - _load_fixed_fares() — 固定運賃データ読み込み（キャッシュ付き、初期化フラグ管理）
  - @tool(context=True) calculate_transport_fare() — 交通費計算ツール関数
  - Pydanticモデル（TransportCalculatorInput）によるバリデーション
  - 戻り値の標準構造（TransportCalculatorOutput対応の辞書）
  - ErrorHandler への委譲によるエラーハンドリング
- **単体テスト内容**:
  - 電車/バス/タクシー/飛行機の正しい運賃返却
  - キャッシュが初回のみ読み込みを行うこと
  - 経路不存在時のエラー返却
  - JSONファイル不存在時のエラー返却
  - 空文字入力時のバリデーションエラー
  - 駅名末尾「駅」除去の正規化動作

---

## タスク14: 申請書生成ツール（output_generator.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/申請書生成ツール詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/10_skeleton_tools.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/tools/output_generator.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_output_generator.py
- **実装内容**:
  - @tool(context=True) generate_expense_report() — 経費精算申請書生成
  - @tool(context=True) generate_transport_report() — 交通費精算申請書生成
  - _generate_form() — 共通フォーム生成ヘルパー（DRY原則、R9.12.1準拠）
  - _write_expense_detail_rows() — 経費明細行書き込み
  - _write_transport_detail_rows() — 移動明細行書き込み
  - invocation_state からの申請者名・申請日取得
  - Pydanticモデルによるバリデーション（ExpenseReportInput / TransportReportInput）
  - output/ ディレクトリへのExcelファイル出力
- **単体テスト内容**:
  - 正しいExcelファイルが生成されること
  - 複数明細が正しく書き込まれること
  - 合計金額が正しく計算されること
  - テンプレート不存在時のエラー返却
  - 空リスト入力時のバリデーションエラー
  - invocation_state欠落時のエラー返却
  - IOError/PermissionError時のエラー返却

---

## タスク15: エージェント共通ユーティリティ（base_agent.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md, artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/17_skeleton_base_agent.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/agents/base_agent.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_base_agent.py
- **実装内容**:
  - calculate_deadline(application_date, deadline_months) — 申請日+月数から期限計算（dateutil.relativedelta）
  - create_specialist_agent() — Session/HumanApprovalHook/LoopControlHook生成+Agent組み立て共通ファクトリ
  - invoke_specialist_agent() — invocation_state取得・deadline計算・Agent呼び出し・例外処理の共通ラッパー
  - LoopLimitError → Exception の2層エラーハンドリング
  - ErrorHandler への委譲
- **単体テスト内容**:
  - calculate_deadline が正しい期限日を返すこと
  - 不正な日付文字列で "要確認" を返すこと
  - create_specialist_agent が Agent インスタンスを返すこと（モック使用）
  - invoke_specialist_agent が LoopLimitError を適切にハンドリングすること
  - invoke_specialist_agent が Exception を適切にハンドリングすること

---

## タスク16: 交通費精算申請エージェント（transport_agent.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/交通費精算申請エージェント詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/12_skeleton_specialist_agent.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/agents/transport_agent.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_transport_agent.py
- **実装内容**:
  - _build_transport_agent(session_id, applicant_name, application_date, deadline) ビルド関数
  - @tool(context=True) transport_agent(query, tool_context) — Agent as Tools ツール関数
  - invoke_specialist_agent() による共通呼び出し（R9.11準拠）
  - settings.transport からエージェント固有パラメータ取得
  - get_transport_system_prompt() によるプロンプト生成
  - tools: [calculate_transport_fare, generate_transport_report]
- **単体テスト内容**:
  - _build_transport_agent が Agent インスタンスを返すこと（モック使用）
  - transport_agent ツール関数が文字列を返すこと
  - invocation_state から正しく情報を取得すること
  - LoopLimitError 時にエラーメッセージを返すこと
  - Exception 時にエラーメッセージを返すこと

---

## タスク17: 経費精算申請エージェント（expense_agent.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/経費精算申請エージェント詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/12_skeleton_specialist_agent.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/agents/expense_agent.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_expense_agent.py
- **実装内容**:
  - _build_expense_agent(session_id, applicant_name, application_date, deadline) ビルド関数
  - @tool(context=True) expense_agent(query, tool_context) — Agent as Tools ツール関数
  - invoke_specialist_agent() による共通呼び出し（R9.11準拠）
  - settings.expense からエージェント固有パラメータ取得
  - get_expense_system_prompt() によるプロンプト生成
  - tools: [generate_expense_report]
- **単体テスト内容**:
  - _build_expense_agent が Agent インスタンスを返すこと（モック使用）
  - expense_agent ツール関数が文字列を返すこと
  - invocation_state から正しく情報を取得すること
  - LoopLimitError 時にエラーメッセージを返すこと
  - Exception 時にエラーメッセージを返すこと

---

## タスク18: 申請受付窓口エージェント（orchestrator_agent.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/11_skeleton_orchestrator_agent.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/agents/orchestrator_agent.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_orchestrator_agent.py
- **実装内容**:
  - OrchestratorAgent クラスの定義
  - __init__(applicant_name) — セッションID生成、初期化
  - _build_agent() — Agent() コンストラクタ（window_size=30, LoopControlHook, callback_handler=None）
  - run() — メインインタラクションループ（ユーザー入力→エージェント呼び出し→応答表示）
  - InvocationState の構築と model_dump() による辞書化
  - tools: [transport_agent, expense_agent]
  - エラーハンドリング（LoopLimitError → Exception の2層構造）
- **単体テスト内容**:
  - OrchestratorAgent が正しく初期化されること
  - _build_agent が Agent インスタンスを返すこと（モック使用）
  - InvocationState が正しく構築されること
  - LoopLimitError 時の適切なエラーハンドリング
  - KeyboardInterrupt 時の適切な終了処理

---

## タスク19: エントリーポイント（main.py）

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/申請受付窓口エージェント詳細設計.md
- **参照するスケルトンコード**: .kiro/artifact-workflow/templates/06_code-generation/13_skeleton_main.md
- **成果物のファイルパス**: artifacts/06_code-generation/src/main.py
- **単体テストコードのファイルパス**: artifacts/06_code-generation/src/tests/unit/test_main.py
- **実装内容**:
  - load_dotenv() による環境変数読み込み
  - 3ハンドラー構成のログ設定（console / app.log / error.log）
  - RotatingFileHandler（10MB × 5世代）
  - ログフォーマット: %(asctime)s [%(levelname)s] %(name)s - %(message)s
  - Strandsライブラリのログレベル制御（WARNING）
  - OrchestratorAgent の生成と run() 呼び出し
  - KeyboardInterrupt / Exception のエラーハンドリング
  - logs/ ディレクトリの自動作成
- **単体テスト内容**:
  - ログ設定が正しく構成されること（ハンドラー数、レベル）
  - OrchestratorAgent が生成されること（モック使用）
  - KeyboardInterrupt 時に適切に終了すること

---

## タスク20: 環境変数テンプレート（.env.template）・プロジェクト設定ファイル

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/03_system-design/outputs/共通設定方針.md
- **参照するスケルトンコード**: なし
- **成果物のファイルパス**:
  - artifacts/06_code-generation/src/.env.template
  - artifacts/06_code-generation/src/pyproject.toml
  - artifacts/06_code-generation/src/.gitignore
- **単体テストコードのファイルパス**: なし
- **実装内容**:
  - .env.template: LOG_LEVEL, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION, GUARDRAIL_ID, GUARDRAIL_VERSION
  - pyproject.toml: 依存パッケージ定義（strands-agents, pydantic, pydantic-settings, openpyxl, python-dotenv, python-dateutil, boto3）、テスト設定（pytest, pytest-cov）
  - .gitignore: .env, logs/, output/, storage/, __pycache__/ 等
- **単体テスト内容**:
  - なし（設定ファイルのため）

---

## タスク21: __init__.py 配置・ディレクトリ構造検証

- **ステータス**: [x] 完了
- **参照する設計書**: なし
- **参照するスケルトンコード**: なし
- **成果物のファイルパス**:
  - artifacts/06_code-generation/src/config/__init__.py
  - artifacts/06_code-generation/src/models/__init__.py
  - artifacts/06_code-generation/src/agents/__init__.py
  - artifacts/06_code-generation/src/handlers/__init__.py
  - artifacts/06_code-generation/src/tools/__init__.py
  - artifacts/06_code-generation/src/prompt/__init__.py
  - artifacts/06_code-generation/src/knowledge/__init__.py
  - artifacts/06_code-generation/src/session/__init__.py
- **単体テストコードのファイルパス**: なし
- **実装内容**:
  - 全パッケージディレクトリに __init__.py を配置
  - ディレクトリ構造が .kiro/steering/00_rule_directory_structure.md（R1）に準拠していることを検証
  - ファイル間の依存関係が R3 に準拠していることを検証
  - ファイル命名規則が R2 に準拠していることを検証
- **単体テスト内容**:
  - なし（構造検証のため）

---

## タスク22: 結合テスト

- **ステータス**: [x] 完了
- **参照する設計書**: artifacts/05_detailed-design/outputs/評価テスト詳細設計.md
- **参照するスケルトンコード**: なし
- **成果物のファイルパス**:
  - artifacts/06_code-generation/src/tests/integration/test_agent_flow.py
  - artifacts/06_code-generation/src/tests/integration/test_tool_integration.py
  - artifacts/06_code-generation/src/tests/integration/test_session_integration.py
- **単体テストコードのファイルパス**: なし（結合テスト自体が成果物）
- **実装内容**:
  - test_agent_flow.py: エージェント間連携テスト（オーケストレーター→専門エージェント振り分け）
  - test_tool_integration.py: ツール連携テスト（交通費計算→申請書生成の一連フロー）
  - test_session_integration.py: セッション永続化テスト（セッション作成→復元→継続）
- **単体テスト内容（結合テスト項目）**:
  - TC-INT-001〜021: エージェント連携、ツール呼び出し、セッション永続化
  - 交通費申請フロー: transport_agent → calculate_transport_fare → generate_transport_report
  - 経費精算フロー: expense_agent → generate_expense_report
  - セッション永続化: 同一セッションIDでの会話継続
  - エラー伝播: 子エージェントのエラーがオーケストレーターに正しく伝播すること