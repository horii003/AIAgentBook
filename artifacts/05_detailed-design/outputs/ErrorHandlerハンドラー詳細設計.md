---
version: "1.0.0"
last_updated: "2026-05-21"
updated_by: ""
---

# ErrorHandler ハンドラー 詳細設計書

> **参照元（基本設計資料）:**
> - artifacts/04_basic-design/outputs/ハンドラー基本設計.md（ErrorHandlerの位置づけ・主要メソッド）

> **参照元（システム設計資料）:**
> - artifacts/03_system-design/outputs/例外処理方針.md（例外処理の全体方針・エラー分類）
> - artifacts/03_system-design/outputs/実行制御方針.md（ループ制御・承認制御の方針）
> - artifacts/03_system-design/outputs/共通設定方針.md（ハンドラーの共通設定）

## 1. 概要

### 1.1 コンポーネントの目的

全エージェント・全ツールで発生する例外を分類し、ユーザー向けの日本語エラーメッセージを生成して返す。技術的な詳細を隠蔽し、ユーザーが理解できる日本語メッセージを返すことが唯一の責務。

### 1.2 主要な責務

- 例外種別ごとのユーザー向けメッセージ生成（文字列を返す）
- 全メソッドを `@staticmethod` として実装（インスタンス化不要）

### 1.3 非責務
- **ログ出力**（各モジュール（エージェント・ツール）が責任を持って行う）
- **セッション状態更新**（FileSessionManager が担当する）
- **例外の再送出**（ツール関数はエラー情報を辞書形式で返す）
- **継続可否判定**（呼び出し元が判断する）

---

## 2. 設計詳細

### 2.1 クラス基本情報

#### クラス名
`ErrorHandler`

#### 説明
例外種別ごとのユーザー向けメッセージを生成するユーティリティクラス。全メソッドが `@staticmethod` であり、インスタンス化不要で `ErrorHandler.handle_xxx()` として直接呼び出す。コンストラクタの引数は持たない。

---

### 2.2 初期化

#### `__init__` は定義しない

`ErrorHandler` はインスタンス変数を持たない。コンストラクタの引数は持たない（`SessionManager` 等の依存注入は行わない）。`logger` インスタンス変数も定義しない。

---

### 2.3 主要メソッド

#### 2.3.1 handle_throttling_error

##### 説明
APIレート制限（ModelThrottledException）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`ModelThrottledException`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### 処理内容
1. ユーザー向けメッセージ文字列を生成して返す

##### メッセージ例
`"システムが混雑しています。しばらく時間をおいて再度お試しください。問題が解決しない場合は申請管理部門にお問い合わせください。"`

---

#### 2.3.2 handle_max_tokens_error

##### 説明
最大トークン数到達（MaxTokensReachedException）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`MaxTokensReachedException`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
`"処理できる情報量の上限に達しました。入力内容を短くして再度お試しください。"`

---

#### 2.3.3 handle_context_window_error

##### 説明
コンテキストウィンドウ超過（ContextWindowOverflowException）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`ContextWindowOverflowException`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
`"会話履歴が長くなりすぎました。新しいセッションで再度お試しください。"`

---

#### 2.3.4 handle_fare_data_error

##### 説明
運賃データ読み込み失敗（FileNotFoundError / Exception）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`FileNotFoundError | Exception`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
- FileNotFoundError: `"運賃データが見つかりませんでした。申請管理部門にお問い合わせください。"`
- Exception: `"運賃データの読み込みに失敗しました。申請管理部門にお問い合わせください。"`

---

#### 2.3.5 handle_calculation_error

##### 説明
運賃計算失敗（Exception）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`Exception`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
`"運賃計算中にエラーが発生しました。申請管理部門にお問い合わせください。"`

---

#### 2.3.6 handle_file_save_error

##### 説明
Excelファイル保存失敗（IOError / PermissionError / Exception）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`IOError | PermissionError | Exception`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
- IOError: `"申請書ファイルの保存に失敗しました。申請管理部門にお問い合わせください。"`
- PermissionError: `"申請書ファイルの保存に失敗しました（権限エラー）。申請管理部門にお問い合わせください。"`
- Exception: `"申請書生成中にエラーが発生しました。申請管理部門にお問い合わせください。"`

---

#### 2.3.7 handle_validation_error

##### 説明
Pydanticバリデーション失敗（ValidationError）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`ValidationError`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
`"入力内容に誤りがあります。{バリデーションエラーの詳細}"`

---

#### 2.3.8 handle_keyboard_interrupt

##### 説明
ユーザーによる中断（KeyboardInterrupt）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`KeyboardInterrupt`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
`"処理を中断しました。"`

---

#### 2.3.9 handle_loop_limit_error

##### 説明
ループ上限到達（LoopLimitError）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`LoopLimitError`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
`"処理の上限に達しました。申請管理部門にお問い合わせください。"`

---

#### 2.3.10 handle_runtime_error

##### 説明
その他の実行時エラー（RuntimeError）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`RuntimeError`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
`"処理中にエラーが発生しました。申請管理部門にお問い合わせください。"`

---

#### 2.3.11 handle_unexpected_error

##### 説明
予期しないエラー（Exception）のユーザー向けメッセージを生成する。

##### 引数
- `e` (`Exception`): 対象例外オブジェクト

##### 戻り値
- `str`: ユーザー向けメッセージ文字列

##### メッセージ例
`"予期しないエラーが発生しました。申請管理部門にお問い合わせください。"`

---

## 3. ビジネスロジック

### 3.1 メソッド一覧

| メソッド名 | 対象例外 | 用途 |
|-----------|---------|------|
| `handle_throttling_error` | `ModelThrottledException` | APIレート制限 |
| `handle_max_tokens_error` | `MaxTokensReachedException` | 最大トークン数到達 |
| `handle_context_window_error` | `ContextWindowOverflowException` | コンテキストウィンドウ超過 |
| `handle_fare_data_error` | `FileNotFoundError / Exception` | 運賃データ読み込み失敗 |
| `handle_calculation_error` | `Exception` | 運賃計算失敗 |
| `handle_file_save_error` | `IOError / PermissionError / Exception` | Excelファイル保存失敗 |
| `handle_validation_error` | `ValidationError` | Pydanticバリデーション失敗 |
| `handle_keyboard_interrupt` | `KeyboardInterrupt` | ユーザーによる中断 |
| `handle_loop_limit_error` | `LoopLimitError` | ループ上限到達 |
| `handle_runtime_error` | `RuntimeError` | その他の実行時エラー |
| `handle_unexpected_error` | `Exception` | 予期しないエラー |

### 3.2 処理フロー

```
呼び出し元で例外発生
  ↓
呼び出し元でログ出力（_logger.error / _logger.warning 等）
  ↓
ErrorHandler.handle_xxx(e) を呼び出す
  ↓
ユーザー向けメッセージ文字列を生成して返す
  ↓
呼び出し元でメッセージを利用（print / 辞書形式で返す 等）
```

---

## 4. エラーハンドリング

### 4.1 処理されるエラー

ErrorHandler 自体はエラーを発生させない。全メソッドは例外を受け取り、文字列を返すのみ。

---

## 5. ログ出力

ErrorHandler クラスのメソッド内ではログ出力を行わない。ログ出力は呼び出し元モジュール（各エージェント・各ツール）が ErrorHandler 呼び出し前に実施する。

---

## 6. 使用例

### 6.1 ツール関数での使用例

```python
from handlers.error_handler import ErrorHandler
from pydantic import ValidationError

@tool
def calculate_transport_fare(departure: str, destination: str, transport_type: str, travel_date: str) -> dict:
    try:
        validated = TransportCalculatorInput(
            departure=departure,
            destination=destination,
            transport_type=transport_type,
            travel_date=travel_date,
        )
    except ValidationError as e:
        _logger.error("バリデーションエラー: %s", e, exc_info=True)
        return {"success": False, "fare": None, "error_message": ErrorHandler.handle_validation_error(e)}
    # ... 処理 ...
```

### 6.2 エージェントでの使用例

```python
from handlers.error_handler import ErrorHandler
from handlers.loop_control_hook import LoopLimitError

try:
    response = self.agent(user_input, invocation_state=invocation_state)
except LoopLimitError as e:
    _logger.warning("ループ上限到達: session_id=%s", self._session_id)
    print(ErrorHandler.handle_loop_limit_error(e))
    continue
except Exception as e:
    _logger.error("予期しないエラー: session_id=%s", self._session_id, exc_info=True)
    print(ErrorHandler.handle_unexpected_error(e))
    continue
```

---

## 7. 補足情報

### 7.1 実装上の注意点

1. **ログ出力の禁止**
   - ErrorHandler クラスのメソッド内でログ出力（`logging.error` / `logging.warning` 等）を行ってはならない
   - ログ出力は呼び出し元の責務

2. **セッション状態更新の禁止**
   - ErrorHandler クラスのメソッド内で SessionManager の呼び出しを行ってはならない

3. **コンストラクタの引数なし**
   - `__init__` に引数を持たせない（`SessionManager` 等の依存注入は行わない）
   - `logger` インスタンス変数を定義しない

4. **外部ライブラリ依存として logging を列挙しない**
   - ErrorHandler は logging を使用しないため、依存関係に列挙しない

---

## 8. 依存関係

### 8.1 外部ライブラリ
- `pydantic`: ValidationError の型参照
  - `ValidationError`
- `strands`: Strands SDK 例外クラスの型参照
  - `ModelThrottledException`, `MaxTokensReachedException`, `ContextWindowOverflowException`

### 8.2 内部モジュール
- `handlers.loop_control_hook`: LoopLimitError の型参照
  - `LoopLimitError`

---

## 9. テスト観点

### 9.1 機能テスト
- `handle_validation_error` が ValidationError を受け取り、日本語メッセージ文字列を返すこと
- `handle_fare_data_error` が FileNotFoundError を受け取り、日本語メッセージ文字列を返すこと
- `handle_file_save_error` が IOError を受け取り、日本語メッセージ文字列を返すこと
- `handle_file_save_error` が PermissionError を受け取り、日本語メッセージ文字列を返すこと
- `handle_loop_limit_error` が LoopLimitError を受け取り、日本語メッセージ文字列を返すこと
- `handle_unexpected_error` が Exception を受け取り、日本語メッセージ文字列を返すこと

### 9.2 異常系テスト
- 各メソッドが None を受け取った場合の動作確認

### 9.3 統合テスト
- ツール関数から ErrorHandler を呼び出し、エラー返却辞書のキー名が Pydantic モデルのフィールド名と一致すること

---

## 10. 設定値

なし（ErrorHandler はインスタンス変数・設定値を持たない）

---

## 11. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-05-21 | 1.0 | 新規作成（修正7反映） |
