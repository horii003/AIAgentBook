---
version: "1.0.0"
last_updated: "2026-05-21"
updated_by: ""
---

# LoopControlHook ハンドラー 詳細設計書

> **参照元（基本設計資料）:**
> - artifacts/04_basic-design/outputs/ハンドラー基本設計.md（LoopControlHookの位置づけ・処理概要）

> **参照元（システム設計資料）:**
> - artifacts/03_system-design/outputs/例外処理方針.md（例外処理の全体方針）
> - artifacts/03_system-design/outputs/実行制御方針.md（ループ制御の方針）
> - artifacts/03_system-design/outputs/共通設定方針.md（ハンドラーの共通設定）

## 1. 概要

### 1.1 コンポーネントの目的

全エージェントの ReActループ回数を監視し、上限（10回）到達時に `LoopLimitError` を発生させる。GRD-007（ループ制限）を実装する。

### 1.2 主要な責務

- エージェント呼び出し開始前にループカウンタをリセットする（BeforeInvocationEvent）
- LLM 呼び出し後にループカウンタをインクリメントし、上限到達を監視する（AfterModelCallEvent）
- エージェント呼び出し完了後に合計ループ回数をログ出力する（AfterInvocationEvent）
- ループ回数を INFO レベルでログ出力する（BeforeModelCallEvent）
- ツール名を INFO レベルでログ出力する（BeforeToolCallEvent / AfterToolCallEvent）
- 上限到達時に `LoopLimitError` を raise する

### 1.3 非責務
- **エラーメッセージ生成**（ErrorHandler が担当する）
- **セッション状態更新**（FileSessionManager が担当する）
- **ユーザーへの通知**（エージェントが担当する）

---

## 2. 設計詳細

### 2.1 クラス基本情報

#### クラス名
`LoopControlHook`

#### 説明
HookProvider を継承してループ制御を実装するフッククラス。全エージェントに登録し、ReActループの無限ループを防止する。

---

### 2.2 LoopLimitError クラス

#### 定義場所
`handlers/loop_control_hook.py`（`LoopControlHook` と同一モジュールに定義する）

#### クラス定義

```python
class LoopLimitError(Exception):
    """ReActループの上限到達を示すカスタム例外クラス。

    Attributes:
        current_iteration (int): 現在のループ回数
        max_iterations (int): 最大ループ回数
        agent_name (str): エージェント名
    """
    def __init__(self, current_iteration: int, max_iterations: int, agent_name: str):
        self.current_iteration = current_iteration
        self.max_iterations = max_iterations
        self.agent_name = agent_name
        super().__init__(
            f"ループ上限到達: {agent_name} が {max_iterations} 回のループ上限に達しました。"
        )
```

**フィールド**:

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `current_iteration` | `int` | 現在のループ回数 |
| `max_iterations` | `int` | 最大ループ回数 |
| `agent_name` | `str` | エージェント名 |

---

### 2.3 初期化

#### `__init__(self, max_iterations: int = 10)`

**引数**:
- `max_iterations` (`int`): 最大ループ回数（デフォルト: 10）

**インスタンス変数**:
- `_max_iterations`: `int` — 最大ループ回数
- `_current_iteration`: `int` — 現在のループ回数（初期値: 0）

---

### 2.4 フック設計

#### 2.4.1 フック登録

##### `register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None`

**登録するイベント**:

| イベント | ハンドラーメソッド | 説明 |
|---------|----------------|------|
| `BeforeInvocationEvent` | `_handle_before_invocation` | ループカウンタをリセットする |
| `BeforeModelCallEvent` | `_handle_before_model_call` | ループ回数をログ出力する |
| `AfterModelCallEvent` | `_handle_after_model_call` | ループカウンタをインクリメントし上限を監視する |
| `BeforeToolCallEvent` | `_handle_before_tool_call` | ツール名をログ出力する |
| `AfterToolCallEvent` | `_handle_after_tool_call` | ツール名をログ出力する |
| `AfterInvocationEvent` | `_handle_after_invocation` | 合計ループ回数をログ出力する |

---

#### 2.4.2 イベントハンドラー

##### _handle_before_invocation

**説明**: エージェント呼び出し開始前にループカウンタを 0 にリセットする

**処理内容**:
1. `self._current_iteration = 0`

---

##### _handle_before_model_call

**説明**: LLM 呼び出し前にループ回数を INFO レベルでログ出力する

**処理内容**:
1. `_logger.info("ループ回数: %d / %d", self._current_iteration + 1, self._max_iterations)`

---

##### _handle_after_model_call

**説明**: LLM 呼び出し後にループカウンタをインクリメントし、上限到達を監視する

**処理内容**:
1. `event.exception` が存在する場合はスキップする（カウントアップしない）
2. `self._current_iteration += 1`
3. `self._current_iteration >= self._max_iterations` の場合:
   - `_logger.warning("ループ上限到達: %d / %d", self._current_iteration, self._max_iterations)`
   - `raise LoopLimitError(current_iteration=self._current_iteration, max_iterations=self._max_iterations, agent_name=event.agent.name if event.agent else "unknown")`

---

##### _handle_before_tool_call

**説明**: ツール実行前にツール名を INFO レベルでログ出力する

**処理内容**:
1. `tool_name = event.tool_use["name"] if event.tool_use else "unknown"`
2. `_logger.info("ツール呼び出し開始: %s", tool_name)`

---

##### _handle_after_tool_call

**説明**: ツール実行後にツール名を INFO レベルでログ出力する

**処理内容**:
1. `tool_name = event.tool_use["name"] if event.tool_use else "unknown"`
2. `_logger.info("ツール呼び出し完了: %s", tool_name)`

---

##### _handle_after_invocation

**説明**: エージェント呼び出し完了後に合計ループ回数を INFO レベルでログ出力する（ループカウンタのリセットは行わない）

**処理内容**:
1. `_logger.info("合計ループ回数: %d", self._current_iteration)`

---

## 3. ビジネスロジック

### 3.1 ループ制御処理フロー

```
BeforeInvocationEvent 発火
  ↓
_current_iteration = 0（リセット）
  ↓
[ReActループ開始]
  ↓
BeforeModelCallEvent 発火
  → _logger.info("ループ回数: {current+1} / {max}")
  ↓
LLM 呼び出し
  ↓
AfterModelCallEvent 発火
  → event.exception が存在する場合はスキップ
  → _current_iteration += 1
  → _current_iteration >= _max_iterations の場合:
    → _logger.warning("ループ上限到達: ...")
    → raise LoopLimitError(current_iteration, max_iterations, agent_name)
  ↓
BeforeToolCallEvent 発火
  → _logger.info("ツール呼び出し開始: {tool_name}")
  ↓
ツール実行
  ↓
AfterToolCallEvent 発火
  → _logger.info("ツール呼び出し完了: {tool_name}")
  ↓
[ReActループ継続 or 終了]
  ↓
AfterInvocationEvent 発火
  → _logger.info("合計ループ回数: {current_iteration}")
  （ループカウンタのリセットは行わない）
```

---

## 4. エラーハンドリング

### 4.1 処理されるエラー

| エラー種別 | 発生条件 | 対応 |
|-----------|---------|------|
| LoopLimitError | ループ回数が max_iterations に達した場合 | raise する（呼び出し元エージェントが捕捉する） |

---

## 5. ログ出力

| レベル | タイミング | メッセージ |
|--------|-----------|-----------|
| INFO | BeforeModelCallEvent 発火時 | `"ループ回数: {current+1} / {max}"` |
| INFO | BeforeToolCallEvent 発火時 | `"ツール呼び出し開始: {tool_name}"` |
| INFO | AfterToolCallEvent 発火時 | `"ツール呼び出し完了: {tool_name}"` |
| INFO | AfterInvocationEvent 発火時 | `"合計ループ回数: {current_iteration}"` |
| WARNING | ループ上限到達時 | `"ループ上限到達: {current_iteration} / {max_iterations}"` |

---

## 6. 使用例

### 6.1 基本的な使用方法

```python
from handlers.loop_control_hook import LoopControlHook, LoopLimitError

# インスタンス作成
hook = LoopControlHook(max_iterations=10)

# Agent() コンストラクタに渡す
agent = Agent(
    ...,
    hooks=[hook]
)
```

### 6.2 LoopLimitError の捕捉

```python
from handlers.loop_control_hook import LoopLimitError
from handlers.error_handler import ErrorHandler

try:
    response = agent(user_input, invocation_state=invocation_state)
except LoopLimitError as e:
    _logger.warning("ループ上限到達: session_id=%s", session_id)
    print(ErrorHandler.handle_loop_limit_error(e))
    continue
```

---

## 7. 補足情報

### 7.1 実装上の注意点

1. **AfterModelCallEvent でのスキップ条件**
   - `event.exception` が存在する場合はカウントアップをスキップする

2. **AfterInvocationEvent でのリセット禁止**
   - `AfterInvocationEvent` のハンドラーではループカウンタのリセットは行わない（合計ループ回数のログ出力のみ）
   - リセットは `BeforeInvocationEvent` のみで行う

3. **LoopLimitError の raise 時のフィールド**
   - `LoopLimitError` を raise する場合、定義済みの全フィールド（`current_iteration`・`max_iterations`・`agent_name`）を引数として渡すこと

4. **LoopLimitError の定義場所**
   - `LoopLimitError` は `handlers/loop_control_hook.py` に定義する
   - 他のモジュールからは `from handlers.loop_control_hook import LoopLimitError` でインポートする

---

## 8. 依存関係

### 8.1 外部ライブラリ
- `strands.hooks`: フックフレームワーク
  - `HookProvider`: フックプロバイダー基底クラス
  - `HookRegistry`: フックレジストリ
  - `BeforeInvocationEvent`: エージェント呼び出し開始前イベント
  - `AfterInvocationEvent`: エージェント呼び出し完了後イベント
  - `BeforeModelCallEvent`: LLM 呼び出し前イベント
  - `AfterModelCallEvent`: LLM 呼び出し後イベント
  - `BeforeToolCallEvent`: ツール実行前イベント
  - `AfterToolCallEvent`: ツール実行後イベント
- `logging`: ログ出力
- `typing`: 型ヒント（`Any`）

### 8.2 内部モジュール
なし（LoopControlHook は外部ライブラリのみに依存する）

---

## 9. テスト観点

### 9.1 機能テスト
- ループ回数が max_iterations 未満の場合に正常に処理が継続されること
- BeforeInvocationEvent 発火時にループカウンタが 0 にリセットされること
- AfterModelCallEvent 発火時にループカウンタがインクリメントされること
- BeforeModelCallEvent 発火時にループ回数が INFO ログに出力されること
- BeforeToolCallEvent 発火時にツール名が INFO ログに出力されること
- AfterToolCallEvent 発火時にツール名が INFO ログに出力されること
- AfterInvocationEvent 発火時に合計ループ回数が INFO ログに出力されること

### 9.2 異常系テスト
- ループ回数が max_iterations に達した場合に LoopLimitError が raise されること
  - **入力**: AfterModelCallEvent を max_iterations 回発火させる
  - **期待結果**: LoopLimitError が raise され、current_iteration・max_iterations・agent_name が正しく設定されていること
- AfterModelCallEvent で event.exception が存在する場合にカウントアップがスキップされること

### 9.3 境界値テスト
- max_iterations=1 の場合に1回目の AfterModelCallEvent で LoopLimitError が raise されること
- max_iterations=10 の場合に10回目の AfterModelCallEvent で LoopLimitError が raise されること

### 9.4 統合テスト
- Agent に LoopControlHook を登録し、ループ上限到達時に LoopLimitError が発生すること

---

## 10. 設定値

### 10.1 ループ制御
- デフォルト最大ループ回数: `10`（GRD-007）

---

## 11. 変更履歴

| 日付 | バージョン | 変更内容 |
|------|-----------|---------|
| 2026-05-21 | 1.0 | 新規作成（修正6反映） |
