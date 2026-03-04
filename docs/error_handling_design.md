# エラーハンドリング設計書

## 1. 概要

本ドキュメントは、社内申請代行エージェントシステム（交通費精算申請・経費精算申請）におけるエラーハンドリング・例外処理の実装方針と内容を整理したものです。設計チームへの設計書作成のインプットとして使用してください。

---

## 2. エラーハンドリングの全体方針

### 2.1 基本方針

- **ログ設定は `main.py` で一元管理**：`logging.basicConfig()` を `main.py` の `_setup_logging()` で呼び出し、アプリケーション全体のログレベル・出力先・フォーマットをここで設定する。各モジュールは `logging.getLogger(__name__)` でロガーを取得するだけでよい
- **ログ出力は各モジュールで実施**：エラーや処理状況のログ出力は、発生箇所に最も近い各モジュールが責任を持って行う
- **ユーザー向けメッセージは `ErrorHandler` で生成**：`handlers/error_handler.py` の `ErrorHandler` クラスにユーザー向けメッセージ生成を集約する。各モジュールはログ出力後に `ErrorHandler` を呼び出してメッセージを取得する
- **ユーザー向けメッセージと技術ログの分離**：ユーザーには平易な日本語メッセージを表示し、技術的な詳細はログに記録する
- **継続性の優先**：可能な限りシステムを継続動作させ、致命的なエラーのみ終了する

### 2.2 エラー伝播の方針

専門エージェントやツールで発生したエラーは、以下の流れでオーケストレーターを経由してユーザーに伝える。

```
fare_tools / excel_generator（ツール）
  └─ エラー発生時：ログ出力 → ErrorHandler でメッセージ生成 → dict で返す
       └─ transportation_expense_agent / receipt_expense_agent（専門エージェント＝@tool）
             └─ ツールの dict 結果を LLM が解釈、またはエラー捕捉時：
                ログ出力 → ErrorHandler でメッセージ生成 → str で返す
                  └─ ReceptionAgent（オーケストレーター）
                        └─ ツール結果の str を受け取り、LLM がユーザーに伝える
                        └─ 自身で捕捉したエラー：ログ出力 → ErrorHandler → print でユーザーに表示
                             └─ main.py
                                   └─ 致命的エラーのみ捕捉：ログ出力 → ErrorHandler → sys.exit
```

**ポイント**：専門エージェントは Strands SDK の `@tool` として実装されているため、エラー時に返した文字列はツール実行結果としてオーケストレーターの LLM コンテキストに渡される。オーケストレーターの LLM がその内容を解釈してユーザーへの応答を生成する。

### 2.3 エラー処理の責務分担

| レイヤー | モジュール | 責務 |
|----------|-----------|------|
| システム起動・終了 | `main.py` | ログ設定、致命的エラーの捕捉と `sys.exit` |
| 対話ループ管理 | `reception_agent.py` | ユーザー入力ループの継続、エラー表示（`print`） |
| 専門エージェント | `transportation_expense_agent.py` / `receipt_expense_agent.py` | エラーをオーケストレーターへ文字列で伝播 |
| ツール | `fare_tools.py` / `excel_generator.py` | エラーを `dict` 形式で返す |
| ループ制御 | `loop_control_hook.py` | ループ上限到達時に `LoopLimitError` を raise |
| メッセージ生成 | `error_handler.py` | ユーザー向けメッセージの生成（全モジュール共通） |

---

## 3. カスタム例外クラス

### 3.1 LoopLimitError（`handlers/error_handler.py`）

| 項目 | 内容 |
|------|------|
| 継承元 | `RuntimeError` |
| 発生箇所 | `LoopControlHook.on_after_model_call()` |
| 目的 | エージェントの ReAct ループが上限回数に達したことを通知する |
| 保持情報 | `current_iteration`（現在回数）、`max_iterations`（上限）、`agent_name`（エージェント名） |

---

## 4. エラーハンドラークラス（`handlers/error_handler.py`）

`ErrorHandler` クラスはユーザー向けメッセージ生成に特化したクラスです。各メソッドは例外オブジェクトを受け取り、日本語のユーザー向けメッセージ文字列を返します。

| メソッド | 対象例外 | 用途 |
|----------|----------|------|
| `handle_throttling_error` | `ModelThrottledException` | API レート制限 |
| `handle_max_tokens_error` | `MaxTokensReachedException` | 最大トークン数到達 |
| `handle_context_window_error` | `ContextWindowOverflowException` | コンテキストウィンドウ超過 |
| `handle_fare_data_error` | `FileNotFoundError` / `Exception` | 運賃データ読み込み失敗 |
| `handle_calculation_error` | `Exception` | 運賃計算失敗 |
| `handle_file_save_error` | `IOError` / `PermissionError` / `Exception` | Excel ファイル保存失敗 |
| `handle_validation_error` | `ValidationError` | Pydantic バリデーション失敗 |
| `handle_keyboard_interrupt` | `KeyboardInterrupt` | ユーザーによる中断 |
| `handle_loop_limit_error` | `LoopLimitError` | ループ上限到達 |
| `handle_runtime_error` | `RuntimeError` | その他の実行時エラー |
| `handle_unexpected_error` | `Exception` | 予期しないエラー |

---

## 5. 各モジュールの例外処理詳細

### 5.1 `main.py`（エントリーポイント）

**役割**：システム全体の起動・終了を管理する最上位のエラーハンドラー

| 例外 | 処理内容 | 終了コード |
|------|----------|-----------|
| `KeyboardInterrupt` | 中断メッセージ表示 | `sys.exit(0)` |
| `ModelThrottledException` | レート制限メッセージ表示 | `sys.exit(1)` |
| `MaxTokensReachedException` | トークン上限メッセージ表示 | `sys.exit(1)` |
| `RuntimeError` | エラーメッセージ表示 | `sys.exit(1)` |
| `Exception`（その他） | 予期しないエラーメッセージ表示 | `sys.exit(1)` |

**ログ設定**：
- レベル：`INFO` 以上
- 出力先：`logs/error.log`（ファイルのみ、コンソール出力あり）
- フォーマット：`%(asctime)s [%(levelname)s] %(name)s - %(message)s`

---

### 5.2 `agents/reception_agent.py`（申請受付窓口エージェント）

**役割**：ユーザーとの対話ループを管理し、エラー発生時も会話を継続する

| 例外 | ログレベル | 処理内容 | 継続/終了 |
|------|-----------|----------|----------|
| `KeyboardInterrupt` | `INFO` | 中断メッセージ表示 | ループ終了（`break`） |
| `LoopLimitError` | `WARNING` | ループ制限メッセージ表示 | 継続（`continue`） |
| `ContextWindowOverflowException` | `WARNING` | コンテキスト超過メッセージ表示 | 継続（`continue`） |
| `MaxTokensReachedException` | `WARNING` | トークン上限メッセージ表示 | 継続（`continue`） |
| `RuntimeError` | `ERROR`（`exc_info=True`） | エラーメッセージ表示 | 継続（`continue`） |
| `Exception`（その他） | `ERROR`（`exc_info=True`） | 予期しないエラーメッセージ表示 | 継続（`continue`） |

**ログ付加情報**：`session_id` をログメッセージに含める

---

### 5.3 `agents/transportation_expense_agent.py` / `agents/receipt_expense_agent.py`（専門エージェント）

**役割**：Agent as Tools として呼び出され、エラー時は文字列メッセージを返す

| 例外 | ログレベル | 処理内容 | 戻り値 |
|------|-----------|----------|--------|
| `LoopLimitError` | `WARNING` | ループ制限メッセージ生成 | エラーメッセージ文字列 |
| `ContextWindowOverflowException` | `WARNING` | コンテキスト超過メッセージ生成 | エラーメッセージ文字列 |
| `MaxTokensReachedException` | `WARNING` | トークン上限メッセージ生成 | エラーメッセージ文字列 |
| `RuntimeError` | `ERROR`（`exc_info=True`） | エラーメッセージ生成 | エラーメッセージ文字列 |
| `Exception`（その他） | `ERROR`（`exc_info=True`） | 予期しないエラーメッセージ生成 | エラーメッセージ文字列 |

**ログ付加情報**：`query`（先頭50文字）をログメッセージに含める

---

### 5.4 `handlers/loop_control_hook.py`（ループ制御フック）

**役割**：エージェントの ReAct ループ回数を監視し、上限超過時に `LoopLimitError` を発生させる

| イベント | 処理内容 |
|----------|----------|
| `BeforeInvocationEvent` | `current_iteration` を 0 にリセット |
| `AfterModelCallEvent` | `current_iteration` をインクリメント。上限到達時に `LoopLimitError` を raise |
| `BeforeModelCallEvent` | ループ回数をログ出力（INFO） |
| `BeforeToolCallEvent` / `AfterToolCallEvent` | ツール名をログ出力（INFO） |
| `AfterInvocationEvent` | 合計ループ回数をログ出力（INFO） |

**上限設定**：
- 申請受付窓口エージェント：`max_iterations=10`
- 交通費精算申請エージェント：`max_iterations=10`
- 経費精算申請エージェント：`max_iterations=10`

**注意**：`AfterModelCallEvent` で `event.exception` が存在する場合はカウントしない（リトライ処理との競合を避けるため）

---

### 5.5 `handlers/human_approval_hook.py`（Human-in-the-Loop 承認フック）

**役割**：Excel 申請書生成ツール実行前にユーザー承認を求める

| 状況 | 処理内容 |
|------|----------|
| 承認（選択肢 1） | ツール実行を継続 |
| 修正要望（選択肢 2） | `event.cancel_tool` に修正要望メッセージをセットしてキャンセル |
| キャンセル（選択肢 3） | `event.cancel_tool` にキャンセルメッセージをセットしてキャンセル |

**対象ツール**：`receipt_excel_generator`、`transportation_excel_generator` のみ

---

### 5.6 `tools/fare_tools.py`（運賃計算ツール）

**役割**：運賃データの読み込みと計算を行い、エラー時は `dict` 形式で結果を返す

#### `load_fare_data()`

| 例外 | ログレベル | 処理内容 | 戻り値 |
|------|-----------|----------|--------|
| ファイル不存在（`os.path.exists` で事前チェック） | `WARNING` | ファイル不存在メッセージ生成 | `(False, エラーメッセージ)` |
| `json.JSONDecodeError` | `ERROR`（`exc_info=True`） | JSON パースエラーメッセージ生成 | `(False, エラーメッセージ)` |
| `Exception`（その他） | `ERROR`（`exc_info=True`） | 予期しないエラーメッセージ生成 | `(False, エラーメッセージ)` |

**ログ付加情報**：`error_type`、ファイルパスを `Context` として付加

#### `calculate_fare()`

| 例外 | ログレベル | 処理内容 | 戻り値 |
|------|-----------|----------|--------|
| `ValidationError`（Pydantic） | `ERROR`（`exc_info=True`） | バリデーションエラーメッセージ生成 | `{"success": False, ...}` |
| 経路未発見（`ValueError`） | `ERROR` | 計算エラーメッセージ生成 | `{"success": False, ...}` |

**ログ付加情報**：`departure`、`destination`、`transport_type`、`date` を `Context` として付加

---

### 5.7 `tools/excel_generator.py`（Excel 申請書生成ツール）

**役割**：Excel ファイルを生成・保存し、エラー時は `dict` 形式で結果を返す

#### `ExcelGeneratorBase._save_workbook()`

| 例外 | ログレベル | 処理内容 | 戻り値 |
|------|-----------|----------|--------|
| `IOError` / `PermissionError` | `ERROR`（`exc_info=True`） | ファイル保存エラーメッセージ生成 | `(False, エラーメッセージ)` |
| `Exception`（その他） | `ERROR`（`exc_info=True`） | 予期しないエラーメッセージ生成 | `(False, エラーメッセージ)` |

#### `ReceiptExcelGenerator.generate()` / `TransportationExcelGenerator.generate()`

| 例外 | ログレベル | 処理内容 | 戻り値 |
|------|-----------|----------|--------|
| `ValidationError`（Pydantic） | `ERROR`（`exc_info=True`） | バリデーションエラーメッセージ生成 | `{"success": False, ...}` |
| `Exception`（その他） | `ERROR`（`exc_info=True`） | 予期しないエラーメッセージ生成 | `{"success": False, ...}` |

**ログ付加情報**：`file_path` をログメッセージに含める

---

## 6. ログ設計

### 6.1 ログ出力先・レベル

`.env` の `LOG_LEVEL` でレベルを制御します。未設定の場合は `WARNING` がデフォルトです。

| 設定 | 内容 |
|------|------|
| `LOG_LEVEL=INFO` | INFO 以上を出力（通常運用） |
| `LOG_LEVEL=DEBUG` | DEBUG 以上を出力（詳細調査時） |
| `LOG_LEVEL=WARNING` | WARNING 以上を出力（最小限） |
| 未設定 | WARNING をデフォルト適用 |

出力先はファイル（`logs/error.log`）とコンソールの両方に常時出力します。

### 6.2 ログフォーマット

```
%(asctime)s [%(levelname)s] %(name)s - %(message)s
```

例：
```
2026-03-04 10:00:00,123 [ERROR] agents.reception_agent - RuntimeError が発生しました: ... | session_id: session_20260304_100000_12345678
```

### 6.3 ログレベルの使い分け

| レベル | 用途 |
|--------|------|
| `INFO` | 正常フロー（エージェント起動、ツール呼び出し、ループ状態） |
| `WARNING` | 回復可能なエラー（LoopLimitError、ContextWindowOverflow、MaxTokens） |
| `ERROR` | 処理失敗（ファイル保存失敗、バリデーションエラー、予期しないエラー） |

### 6.4 ログに含める付加情報

| モジュール | 付加情報 |
|-----------|----------|
| `reception_agent` | `session_id` |
| `transportation_expense_agent` / `receipt_expense_agent` | `query`（先頭50文字） |
| `fare_tools` | `departure`、`destination`、`transport_type`、`date` |
| `excel_generator` | `file_path` |
| `loop_control_hook` | `agent_name`、ループ回数 |

---

## 7. Pydantic バリデーション

入力データの整合性チェックに Pydantic モデルを使用しています。

| 使用箇所 | モデル | 目的 |
|----------|--------|------|
| `reception_agent.py` | `InvocationState` | `invocation_state` の型チェック |
| `fare_tools.py` | `FareCalculationInput`、`FareData`、`TrainFareRoute` | 運賃計算入力・データの検証 |
| `excel_generator.py` | `RouteInput`、`ReceiptExpenseInput`、`InvocationState` | Excel 生成入力データの検証 |

バリデーションエラー（`ValidationError`）は `ErrorHandler.handle_validation_error()` で処理し、ユーザー向けメッセージを返します。

---

## 8. リトライ戦略

Amazon Bedrock API 呼び出しのリトライは Strands SDK の `ModelRetryStrategy` で管理します。

| 設定項目 | 値 |
|----------|-----|
| `max_attempts` | 6 |
| `initial_delay` | 4 秒 |
| `max_delay` | 240 秒 |

全エージェント（申請受付窓口、交通費精算申請、経費精算申請）に同一設定を適用しています。

---

## 9. 未対応・今後の検討事項

| 項目 | 内容 |
|------|------|
| エラー通知 | 重大エラー発生時のメール・Slack 通知などの外部通知機能は未実装 |
| エラー統計 | エラー発生頻度の集計・モニタリング機能は未実装 |
| セッション復元 | エラー後のセッション状態復元機能は未実装（現状はリセットのみ） |
