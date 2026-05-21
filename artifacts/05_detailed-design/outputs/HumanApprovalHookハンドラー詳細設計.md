---
version: "1.0.0"
last_updated: "2026-05-21"
updated_by: ""
---

# HumanApprovalHook ハンドラー 詳細設計書

> **参照元（基本設計資料）:**
> - artifacts/04_basic-design/outputs/ハンドラー基本設計.md（HumanApprovalHookの位置づけ・処理概要）

> **参照元（システム設計資料）:**
> - artifacts/03_system-design/outputs/例外処理方針.md（例外処理の全体方針）
> - artifacts/03_system-design/outputs/実行制御方針.md（承認制御の方針）
> - artifacts/03_system-design/outputs/共通設定方針.md（ハンドラーの共通設定）

## 1. 概要

### 1.1 コンポーネントの目的

申請書生成ツール（`generate_transport_expense_form` / `generate_general_expense_form`）が呼び出される前にユーザーの承認を求める。GRD-008（申請書生成前確認）を実装する。

### 1.2 主要な責務

- 申請書生成ツール呼び出し前（BeforeToolCallEvent）にユーザーの承認を求める
- 承認コールバック関数を呼び出し、結果に応じてツール実行を継続・キャンセルする
- 対象外ツールの呼び出し時はスキップする

### 1.3 非責務
- **申請書の提出**（BRL-06 に従い、提出は人が実行する）
- **ループ制御**（LoopControlHook が担当する）
- **エラーメッセージ生成**（ErrorHandler が担当する）

---

## 2. 設計詳細

### 2.1 クラス基本情報

#### クラス名
`HumanApprovalHook`

#### 説明
HookProvider を継承して人間承認制御を実装するフッククラス。AG-002・AG-003 に登録し、申請書生成前のユーザー承認を実現する。

---

### 2.2 初期化

#### `__init__(self, approval_callback)`

**引数**:
- `approval_callback`: 承認コールバック関数

**インスタンス変数**:
- `_approval_callback`: 承認コールバック関数
- `_target_tools`: `set[str]` — 承認対象ツール名のセット

**承認対象ツール名**:
```python
_target_tools = {"generate_transport_expense_form", "generate_general_expense_form"}
```

---

### 2.3 承認コールバック仕様

#### シグネチャ

```python
def approval_callback(tool_name: str, tool_params: dict) -> tuple[bool, str]:
    ...
```

#### 引数
- `tool_name` (`str`): 呼び出されるツール名
- `tool_params` (`dict`): ツールへの入力パラメータ

#### 戻り値

| 戻り値 | 意味 | 処理 |
|-------|------|------|
| `(True, "")` | OK（承認） | 何もしない → ツール実行される |
| `(False, "修正内容")` | 修正要望 | `event.cancel_tool` にメッセージをセット → ツールキャンセル |
| `(False, "CANCEL")` | キャンセル | `event.cancel_tool` にキャンセルメッセージをセット → ツールキャンセル |

---

### 2.4 フック設計

#### 2.4.1 フック登録

##### `register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None`

**登録するイベント**:

| イベント | ハンドラーメソッド | 説明 |
|---------|----------------|------|
| `BeforeToolCallEvent` | `_handle_before_tool_call` | 申請書生成ツール呼び出し前に承認を求める |

---

#### 2.4.2 イベントハンドラー

##### _handle_before_tool_call

**説明**: ツール実行前に発火する。対象ツールのみにフィルタリングして承認コールバックを呼び出す。

**処理内容**:
1. `tool_name = event.tool_use["name"] if event.tool_use else "unknown"`
2. `tool_name not in self._target_tools` の場合はスキップ（return）
3. `tool_params = event.tool_use["input"] or {}` でツール入力パラメータを取得
4. `approved, message = self._approval_callback(tool_name, tool_params)` を呼び出す
5. `approved=True` の場合: 何もしない（ツール実行を継続）
6. `approved=False` かつ `message == "CANCEL"` の場合:
   - `event.cancel_tool = "申請書生成をキャンセルしました。"`
7. `approved=False` かつ `message != "CANCEL"` の場合（修正要望）:
   - `event.cancel_tool = message`（修正内容をキャンセルメッセージとして設定）

---

## 3. ビジネスロジック

### 3.1 承認制御処理フロー

```
AG-002/AG-003 が申請書ドラフトをテキストで提示する（ツール呼び出しなし）
  ↓
AG-002/AG-003 が generate_transport_expense_form / generate_general_expense_form を呼び出そうとする
  ↓
BeforeToolCallEvent 発火
  ↓
_handle_before_tool_call が呼び出される
  ↓
tool_name が _target_tools に含まれるか確認
  - 含まれない場合: スキップ（return）
  ↓
tool_params を取得する
  ↓
_approval_callback(tool_name, tool_params) を呼び出す
  ↓
[承認結果の分岐]
  ↓
(True, "") → 何もしない → ツール実行される
  ↓
(False, "CANCEL") → event.cancel_tool = "申請書生成をキャンセルしました。" → ツールキャンセル
  ↓
(False, "修正内容") → event.cancel_tool = "修正内容" → ツールキャンセル
```

---

## 4. エラーハンドリング

### 4.1 処理されるエラー

| エラー種別 | 発生条件 | 対応 |
|-----------|---------|------|
| なし | — | HumanApprovalHook 自体はエラーを発生させない |

---

## 5. ログ出力

| レベル | タイミング | メッセージ |
|--------|-----------|-----------|
| INFO | 承認コールバック呼び出し時 | `"申請書生成承認確認: tool_name={tool_name}"` |
| INFO | 承認（OK）時 | `"申請書生成承認: tool_name={tool_name}"` |
| INFO | キャンセル時 | `"申請書生成キャンセル: tool_name={tool_name}"` |
| INFO | 修正要望時 | `"申請書生成修正要望: tool_name={tool_name}"` |

---

## 6. 使用例

### 6.1 基本的な使用方法

```python
from handlers.human_approval_hook import HumanApprovalHook

def approval_callback(tool_name: str, tool_params: dict) -> tuple[bool, str]:
    """承認コールバック関数。ユーザーに承認を求める。"""
    print(f"\n申請書を生成しますか？ [OK / 修正 / キャンセル]")
    choice = input("選択: ").strip()
    if choice.upper() == "OK":
        return (True, "")
    elif choice.upper() == "キャンセル":
        return (False, "CANCEL")
    else:
        return (False, choice)  # 修正内容をそのまま返す

# インスタンス作成
hook = HumanApprovalHook(approval_callback=approval_callback)

# Agent() コンストラクタに渡す
agent = Agent(
    ...,
    hooks=[hook, LoopControlHook(max_iterations=10)]
)
```

---

## 7. 補足情報

### 7.1 実装上の注意点

1. **ツール中止方法**
   - `event.stop_reason` ではなく `event.cancel_tool` にメッセージ文字列をセットする
   - `event.cancel()` は存在しない

2. **対象ツールのフィルタリング**
   - BeforeToolCallEvent は全ツール呼び出しで発火するため、`_target_tools` でフィルタリングすること

3. **承認対象ツール名**
   - 申請書生成ツール詳細設計書に定義された全ツール関数名（`generate_transport_expense_form` / `generate_general_expense_form`）を対象とする

4. **承認コールバックの戻り値**
   - `(True, "")`: OK → ツール実行継続
   - `(False, "修正内容")`: 修正要望 → `event.cancel_tool` に修正内容をセット
   - `(False, "CANCEL")`: キャンセル → `event.cancel_tool` にキャンセルメッセージをセット

---

## 8. 依存関係

### 8.1 外部ライブラリ
- `strands.hooks`: フックフレームワーク
  - `HookProvider`: フックプロバイダー基底クラス
  - `HookRegistry`: フックレジストリ
  - `BeforeToolCallEvent`: ツール実行前イベント
- `logging`: ログ出力
- `typing`: 型ヒント（`Any`, `Callable`）

### 8.2 内部モジュール
なし（HumanApprovalHook は外部ライブラリのみに依存する）

---

## 9. テスト観点

### 9.1 機能テスト
- 承認コールバックが `(True, "")` を返した場合にツール実行が継続されること
  - **入力**: `approval_callback` が `(True, "")` を返す
  - **期待結果**: `event.cancel_tool` が設定されないこと
- 承認コールバックが `(False, "CANCEL")` を返した場合にツール実行がキャンセルされること
  - **入力**: `approval_callback` が `(False, "CANCEL")` を返す
  - **期待結果**: `event.cancel_tool = "申請書生成をキャンセルしました。"` が設定されること
- 承認コールバックが `(False, "修正内容")` を返した場合にツール実行がキャンセルされること
  - **入力**: `approval_callback` が `(False, "移動日を修正してください")` を返す
  - **期待結果**: `event.cancel_tool = "移動日を修正してください"` が設定されること
- 対象外ツールの呼び出し時にフックがスキップされること
  - **入力**: `tool_name = "calculate_transport_fare"`
  - **期待結果**: `_approval_callback` が呼び出されないこと

### 9.2 異常系テスト
- `event.tool_use` が None の場合にスキップされること

### 9.3 統合テスト
- AG-002 に HumanApprovalHook を登録し、`generate_transport_expense_form` 呼び出し前に承認コールバックが呼び出されること
- AG-003 に HumanApprovalHook を登録し、`generate_general_expense_form` 呼び出し前に承認コールバックが呼び出されること

---

## 10. 設定値

### 10.1 承認対象ツール名
- `generate_transport_expense_form`
- `generate_general_expense_form`

---

## 11. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-05-21 | 1.0 | 新規作成（修正2,8反映） |
