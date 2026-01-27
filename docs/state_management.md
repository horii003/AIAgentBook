# invocation_state による申請者情報の管理

## 概要

Strands Agentの`invocation_state`機能を利用して、申請者名をセッション全体で管理する実装です。
`invocation_state`は、エージェント呼び出し時のコンテキスト情報を渡すために設計された機能で、親エージェントから子エージェント、さらにツールまで自動的に伝播します。

## アーキテクチャ

```
┌─────────────────────────────────────────┐
│     ReceptionAgent (親エージェント)      │
│  - _applicant_name に申請者名を保持      │
│  - agent()呼び出し時にinvocation_state   │
│    として渡す                             │
└─────────────────────────────────────────┘
              │
              │ agent(query, applicant_name="山田太郎")
              │
              ├─────────────────┬──────────────────┐
              ▼                 ▼                  ▼
    ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
    │ TravelAgent      │ │ReceiptExpenseAgent│ │ (Future Agents)  │
    │ (子エージェント)  │ │ (子エージェント)   │ │                  │
    │ - invocation_state│ │ - invocation_state│ │                  │
    │   で受け取る      │ │   で受け取る       │ │                  │
    └──────────────────┘ └──────────────────┘ └──────────────────┘
              │                 │
              ▼                 ▼
    ┌──────────────────────────────────────┐
    │  Tools (ToolContext経由でアクセス)    │
    │  - travel_excel_generator            │
    │    → invocation_state から取得        │
    │  - receipt_excel_generator           │
    │    → invocation_state から取得        │
    └──────────────────────────────────────┘
```

## 実装詳細

### 1. ReceptionAgent（親エージェント）

**ファイル**: `agents/reception_agent.py`

#### 変更点

1. **インスタンス変数で申請者名を保持**
   ```python
   def __init__(self):
       self.agent = Agent(...)
       self._applicant_initialized = False
       self._applicant_name = None  # 申請者名を保持
   ```

2. **申請者情報の初期化メソッド**
   ```python
   def _initialize_applicant_info(self):
       """申請者情報を初期化"""
       if self._applicant_initialized:
           return
       
       # ユーザーから申請者名を入力
       applicant_name = input("申請者名を入力してください: ").strip()
       
       # インスタンス変数に保存
       self._applicant_name = applicant_name
       self._applicant_initialized = True
   ```

3. **エージェント呼び出し時にinvocation_stateとして渡す**
   ```python
   def run(self):
       # ... 初期化処理
       
       while True:
           user_input = input("入力内容: ")
           
           # invocation_stateとして申請者名を渡す
           response = self.agent(user_input, applicant_name=self._applicant_name)
   ```

4. **リセット処理**
   ```python
   if user_input.lower() in ["reset", "リセット", "最初から"]:
       reset_travel_agent()
       reset_receipt_expense_agent()
       self._applicant_name = None
       self._applicant_initialized = False
       # ... 再初期化
   ```

### 2. 子エージェント（TravelAgent, ReceiptExpenseAgent）

**ファイル**: 
- `agents/travel_agent.py`
- `agents/receipt_expense_agent.py`

#### 変更点

1. **ToolContextのインポート**
   ```python
   from strands import Agent, tool, ToolContext
   ```

2. **Agent as Toolsの関数で@tool(context=True)を使用**
   ```python
   @tool(context=True)
   def travel_agent(query: str, tool_context: ToolContext) -> str:
       # エージェントインスタンスを取得
       agent = _get_travel_agent()
       
       # invocation_stateから申請者名を取得
       applicant_name = None
       if tool_context and tool_context.invocation_state:
           applicant_name = tool_context.invocation_state.get("applicant_name")
       
       # 子エージェントを実行（invocation_stateを渡す）
       if applicant_name:
           response = agent(query, applicant_name=applicant_name)
       else:
           response = agent(query)
       
       return str(response)
   ```

3. **システムプロンプトを更新**
   - 申請者情報が自動取得されることを明記
   - ツール呼び出し時に申請者情報の引数が不要であることを説明

### 3. Tools（excel_generator）

**ファイル**: `tools/excel_generator.py`

#### 変更点

1. **ToolContextのインポート**
   ```python
   from strands import tool, ToolContext
   ```

2. **receipt_excel_generator の変更**
   - `@tool` → `@tool(context=True)` に変更
   - `tool_context` パラメータを追加
   - invocation_stateから申請者名を取得
   ```python
   @tool(context=True)
   def receipt_excel_generator(
       store_name: str,
       amount: float,
       date: str,
       items: List[str],
       expense_category: str,
       tool_context
   ) -> dict:
       # invocation_stateから申請者名を取得
       applicant_name = tool_context.invocation_state.get("applicant_name", "未設定") \
           if tool_context.invocation_state else "未設定"
       # ... 処理続行
   ```

3. **travel_excel_generator の変更**
   - `@tool` → `@tool(context=True)` に変更
   - `tool_context` パラメータを追加
   - invocation_stateから申請者名を取得
   ```python
   @tool(context=True)
   def travel_excel_generator(
       routes: List[dict],
       tool_context
   ) -> dict:
       # invocation_stateから申請者名を取得
       applicant_name = tool_context.invocation_state.get("applicant_name", "未設定") \
           if tool_context.invocation_state else "未設定"
       # ... 処理続行
   ```

## invocation_state の構造

```python
# エージェント呼び出し時
agent(query, applicant_name="山田太郎")

# ↓ 内部的には以下のような構造
# invocation_state = {
#     "applicant_name": "山田太郎"
# }
```

## 利用フロー

### 1. 初回起動時

```
1. ユーザーがmain.pyを実行
2. ReceptionAgentが起動
3. _initialize_applicant_info()が呼ばれる
4. ユーザーに申請者名の入力を促す
5. 入力された情報をインスタンス変数(_applicant_name)に保存
6. 通常の対話ループに入る
```

### 2. 申請書生成時

```
1. ユーザーが申請内容を入力
2. ReceptionAgentがLLMに問い合わせ
3. agent(query, applicant_name=self._applicant_name) でinvocation_stateとして渡す
4. 子エージェント（travel_agent/receipt_expense_agent）が呼ばれる
5. 子エージェントがinvocation_stateから申請者名を取得
6. 子エージェントが自身のエージェントを呼び出す際にinvocation_stateを渡す
7. ツールがinvocation_stateから申請者名を取得
8. 申請書に申請者情報を記載して生成
```

### 3. リセット時

```
1. ユーザーが "reset" と入力
2. 子エージェントの会話履歴をクリア
3. _applicant_name をクリア
4. _applicant_initializedフラグをFalseに設定
5. _initialize_applicant_info()を再度呼び出し
6. 新しい申請者情報を入力
```

## 利点

### ✅ セッション全体で申請者情報を保持
- 一度入力すれば、複数の申請で再利用可能
- ユーザーの入力負担を軽減

### ✅ 自動的に伝播
- invocation_stateは親→子→ツールまで自動的に伝播
- 明示的なコピー処理が不要

### ✅ ツールから簡単にアクセス
- ToolContextを使えば、どのツールからでもアクセス可能
- コードの可読性が向上

### ✅ Strandsの設計思想に沿っている
- invocation_stateは「呼び出し時のコンテキスト」を渡すために設計されている
- agent.stateは「エージェント自身の状態」を保持するためのもの

### ✅ シンプルで理解しやすい
- stateの複製処理が不要
- 「呼び出し時に渡す情報」という明確な概念

## 注意事項

### invocation_stateの伝播
- 親エージェントから子エージェントへ自動的に伝播
- 子エージェントからツールへも自動的に伝播
- 各レベルで明示的に渡す必要がある（自動継承ではない）

### ToolContextの使用
- `@tool(context=True)` デコレータを使用する必要がある
- パラメータ名は `tool_context` である必要がある（Strands Agentの仕様）

### デフォルト値
- invocation_stateから値が取得できない場合のデフォルト値を設定
  - `applicant_name`: "未設定"

## テスト方法

### 1. 基本フロー
```bash
cd AIAgentBook
python main.py
```

入力例:
```
申請者名を入力してください: 山田太郎
入力内容(終了時は'quit'): 交通費の申請をしたいです
```

### 2. リセット機能
```
入力内容(終了時は'quit'): reset
申請者名を入力してください: 佐藤花子
```

### 3. State確認（デバッグ用）
```python
# reception_agent.py の run() メソッド内で確認
print(f"Current state: {self.agent.state.get()}")
```

## 今後の拡張可能性

### 追加情報の管理
- 部署名
- メールアドレス
- 承認者情報

### マルチユーザー対応
- ユーザーIDごとに情報を管理
- データベースとの連携

### セッション永続化
- invocation_stateの内容をファイルに保存
- 次回起動時に前回のセッションを復元

## 関連ドキュメント

- [invocation_state の完全ガイド](./invocation_state_guide.md) - invocation_stateの詳細な使い方と実装例

