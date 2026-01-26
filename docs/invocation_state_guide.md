# invocation_state の完全ガイド

## 概要

このドキュメントでは、Strands Agentの`invocation_state`機能を使って、申請者名がどのように渡され、最終的にExcelファイルに書き込まれるまでの流れを詳しく説明します。

## invocation_state とは

`invocation_state`は、エージェント呼び出し時に渡すコンテキスト情報です。

**Strands公式ドキュメントより**:
> invocation_state: Use for context and configuration that should not appear in prompts but affects tool behavior. Best suited for parameters that can change between agent invocations. Examples include user IDs for personalization, session IDs, or user flags.

### agent.state との違い

| 特徴 | invocation_state | agent.state |
|------|------------------|-------------|
| **用途** | 呼び出し時のコンテキスト | エージェント自身の状態 |
| **保持期間** | 1回の呼び出しのみ | エージェントのライフサイクル全体 |
| **伝播** | 親→子→ツールまで自動伝播 | 自動継承されない |
| **設定方法** | `agent(query, key=value)` | `agent.state.set(key, value)` |
| **取得方法** | `tool_context.invocation_state.get(key)` | `agent.state.get(key)` |
| **適用例** | ユーザーID、セッションID、リクエスト固有の情報 | エージェントの内部状態、学習データ |

---

## 全体の流れ（シンプル版）

```
1. ユーザーが申請者名を入力
   ↓
2. ReceptionAgent（親）のインスタンス変数に保存
   ↓
3. agent()呼び出し時にinvocation_stateとして渡す
   ↓
4. 子エージェント（TravelAgent/ReceiptExpenseAgent）が呼ばれる
   ↓
5. 子エージェントがinvocation_stateから申請者名を取得
   ↓
6. 子エージェントが自身のagent()を呼び出す際にinvocation_stateを渡す
   ↓
7. ツール（excel_generator）が呼ばれる
   ↓
8. ツールがinvocation_stateから申請者名を取得
   ↓
9. Excel申請書に申請者名を書き込む
```

---

## 詳細な流れ（コード付き）

### ステップ1: ユーザーが申請者名を入力

**場所**: `agents/reception_agent.py` の `_initialize_applicant_info()` メソッド

```python
def _initialize_applicant_info(self):
    """申請者情報を初期化"""
    # ユーザーに入力を促す
    applicant_name = input("申請者名を入力してください: ").strip()
    # 例: ユーザーが「山田太郎」と入力
```

**実行例**:
```
申請者名を入力してください: 山田太郎
```

---

### ステップ2: ReceptionAgent（親）のインスタンス変数に保存

**場所**: `agents/reception_agent.py` の `_initialize_applicant_info()` メソッド

```python
# インスタンス変数に保存
self._applicant_name = applicant_name
# ↓ 内部的には以下のような状態
# self._applicant_name = "山田太郎"
```

**ポイント**:
- `self._applicant_name` はReceptionAgentのインスタンス変数
- agent.stateではなく、通常のPythonインスタンス変数として保持
- この時点では親エージェントのみがこの情報を持っている

---

### ステップ3: agent()呼び出し時にinvocation_stateとして渡す

**場所**: `agents/reception_agent.py` の対話ループ内

```python
# ユーザーが「交通費の申請をしたい」と入力した場合
user_input = "交通費の申請をしたい"

# ★ここが重要★
# invocation_stateとして申請者名を渡す
response = self.agent(user_input, applicant_name=self._applicant_name)
# ↓ 内部的には以下のような構造
# invocation_state = {
#     "applicant_name": "山田太郎"
# }
```

**ポイント**:
- `agent(query, key=value)` の形式で、キーワード引数として渡す
- 渡された値は自動的に`invocation_state`として扱われる
- ReceptionAgentのLLMが、ユーザーの入力から適切な子エージェント（ツール）を選択

---

### ステップ4: 子エージェントが呼ばれる

**場所**: `agents/travel_agent.py` の `travel_agent()` 関数

```python
@tool(context=True)
def travel_agent(query: str, tool_context: ToolContext) -> str:
    """交通費精算申請ツール"""
    
    # 子エージェントのインスタンスを取得
    agent = _get_travel_agent()
    
    # ★ここが重要★
    # tool_contextを通じてinvocation_stateにアクセス
    applicant_name = None
    if tool_context and tool_context.invocation_state:
        # invocation_stateから申請者名を取得
        applicant_name = tool_context.invocation_state.get("applicant_name")
        # applicant_name = "山田太郎"
```

**ポイント**:
- `@tool(context=True)` により、`tool_context` パラメータが自動的に渡される
- `tool_context.invocation_state` で親から渡されたinvocation_stateにアクセス
- `tool_context.invocation_state.get("applicant_name")` で値を取得

**図解**:
```
┌─────────────────────────────┐
│  ReceptionAgent (親)         │
│  agent(query,               │
│    applicant_name="山田太郎")│
└─────────────────────────────┘
              ↓ invocation_state として伝播
┌─────────────────────────────┐
│  travel_agent (ツール関数)   │
│  tool_context.invocation_state│
│    .get("applicant_name")   │
│  = "山田太郎"                │
└─────────────────────────────┘
```

---

### ステップ5: 子エージェントが自身のagent()を呼び出す際にinvocation_stateを渡す

**場所**: `agents/travel_agent.py` の `travel_agent()` 関数（続き）

```python
    # 子エージェントを実行（invocation_stateを渡す）
    if applicant_name:
        response = agent(query, applicant_name=applicant_name)
    else:
        response = agent(query)
    
    return str(response)
```

**ポイント**:
- `agent` は子エージェント（TravelAgent）のインスタンス
- 親から取得した申請者名を、子エージェントの呼び出し時にinvocation_stateとして渡す
- これにより、子エージェントのツール（excel_generator）がinvocation_stateにアクセスできる

**図解**:
```
┌─────────────────────────────┐
│  travel_agent (ツール関数)   │
│  applicant_name = "山田太郎" │
└─────────────────────────────┘
              ↓ agent(query, applicant_name=applicant_name)
┌─────────────────────────────┐
│  TravelAgent (子)           │
│  invocation_state = {       │
│    "applicant_name": "山田太郎"│
│  }                          │
└─────────────────────────────┘
```

---

### ステップ6: ツール（excel_generator）が呼ばれる

**場所**: `agents/travel_agent.py` の内部処理

```python
# TravelAgentのLLMが、ユーザーの入力から経路情報を収集
# すべての経路情報が揃ったら、travel_excel_generatorツールを呼び出す

# 例: LLMが以下のようなツール呼び出しを生成
# travel_excel_generator(routes=[
#     {"departure": "東京", "destination": "大阪", "date": "2026-01-26", 
#      "transport_type": "train", "cost": 13620}
# ])
```

**ポイント**:
- TravelAgentのLLMが、適切なタイミングで `travel_excel_generator` ツールを呼び出す
- この時、`tool_context` が自動的にツールに渡される
- `tool_context.invocation_state` には親から渡された情報が含まれている

---

### ステップ7: ツールがinvocation_stateから申請者名を取得

**場所**: `tools/excel_generator.py` の `travel_excel_generator()` 関数

```python
@tool(context=True)
def travel_excel_generator(
    routes: List[dict],
    tool_context
) -> dict:
    """交通費申請書をExcel形式で生成する"""
    
    # ★ここが重要★
    # tool_contextを通じてinvocation_stateにアクセス
    applicant_name = tool_context.invocation_state.get("applicant_name", "未設定") \
        if tool_context.invocation_state else "未設定"
    # applicant_name = "山田太郎"
    
    # ... Excel生成処理 ...
```

**ポイント**:
- `@tool(context=True)` により、`tool_context` パラメータが自動的に渡される
- `tool_context.invocation_state` で子エージェントから渡されたinvocation_stateにアクセス
- `tool_context.invocation_state.get("applicant_name", "未設定")` で値を取得
- 値が取得できない場合は `"未設定"` をデフォルト値として使用

**図解**:
```
┌─────────────────────────────┐
│  TravelAgent (子)           │
│  invocation_state = {       │
│    "applicant_name": "山田太郎"│
│  }                          │
└─────────────────────────────┘
              ↓ tool_context.invocation_state.get("applicant_name")
┌─────────────────────────────┐
│  travel_excel_generator     │
│  applicant_name = "山田太郎" │
└─────────────────────────────┘
```

---

### ステップ8: Excel申請書に申請者名を書き込む

**場所**: `tools/excel_generator.py` の `travel_excel_generator()` 関数（続き）

```python
    # Excelワークブックの作成
    wb = Workbook()
    ws = wb.active
    ws.title = "交通費申請書"
    
    # ... スタイル定義 ...
    
    # タイトル行
    ws["A1"] = "交通費申請書"
    
    # 申請者情報の作成
    current_row = 3
    
    # 申請者名を書き込む
    ws[f"A{current_row}"] = "申請者名"
    ws[f"B{current_row}"] = applicant_name  # ← "山田太郎" が書き込まれる
    
    # ... 残りの処理 ...
    
    # ファイル保存
    wb.save(file_path)
```

**ポイント**:
- `applicant_name` 変数に格納された値（"山田太郎"）がExcelのセルに書き込まれる
- これにより、生成されたExcel申請書に正しい申請者名が表示される

**生成されるExcel**:
```
┌──────────────────────────────────────┐
│         交通費申請書                  │
├──────────────┬───────────────────────┤
│ 申請者名      │ 山田太郎               │
│ 申請日        │ 2026-01-26            │
├──────────────┴───────────────────────┤
│ No │ 日付 │ 出発地 │ 目的地 │ ...    │
└──────────────────────────────────────┘
```

---

## 重要なポイントまとめ

### 1. invocation_stateの渡し方

```python
# エージェント呼び出し時にキーワード引数として渡す
response = agent(query, key1=value1, key2=value2)

# 例
response = self.agent(user_input, applicant_name="山田太郎")
```

### 2. invocation_stateの取得方法

```python
# ToolContext経由でアクセス
@tool(context=True)
def my_tool(param: str, tool_context: ToolContext) -> str:
    # invocation_stateから値を取得
    value = tool_context.invocation_state.get("key", "デフォルト値") \
        if tool_context.invocation_state else "デフォルト値"
    
    return f"取得した値: {value}"
```

### 3. invocation_stateの伝播

```python
# 親エージェント
parent_agent(query, applicant_name="山田太郎")
  ↓ 自動的に伝播
# 子エージェントのツール関数
@tool(context=True)
def child_agent(query, tool_context):
    name = tool_context.invocation_state.get("applicant_name")
    # 子エージェントを呼び出す際に明示的に渡す
    agent(query, applicant_name=name)
      ↓ 自動的に伝播
# Excel生成ツール
@tool(context=True)
def excel_generator(routes, tool_context):
    name = tool_context.invocation_state.get("applicant_name")
```

---

## 実際のコード例（完全版）

### 親エージェント（ReceptionAgent）

```python
class ReceptionAgent:
    def __init__(self):
        self.agent = Agent(...)
        self._applicant_initialized = False
        self._applicant_name = None  # 申請者名を保持
    
    def _initialize_applicant_info(self):
        """申請者情報を初期化"""
        if self._applicant_initialized:
            return
        
        # ユーザー入力
        applicant_name = input("申請者名を入力してください: ").strip()
        
        # インスタンス変数に保存
        self._applicant_name = applicant_name
        self._applicant_initialized = True
        
        print(f"申請者情報を登録しました: {applicant_name}")
    
    def run(self):
        # 初期化
        self._initialize_applicant_info()
        
        # 対話ループ
        while True:
            user_input = input("入力内容: ")
            
            # invocation_stateとして申請者名を渡す
            response = self.agent(user_input, applicant_name=self._applicant_name)
            print(f"エージェント: {response}")
```

### 子エージェントのツール関数（TravelAgent）

```python
@tool(context=True)
def travel_agent(query: str, tool_context: ToolContext) -> str:
    """交通費精算申請ツール"""
    
    # 子エージェントのインスタンスを取得
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

### Excel生成ツール

```python
@tool(context=True)
def travel_excel_generator(
    routes: List[dict],
    tool_context
) -> dict:
    """交通費申請書をExcel形式で生成する"""
    
    # invocation_stateから申請者名を取得
    applicant_name = tool_context.invocation_state.get("applicant_name", "未設定") \
        if tool_context.invocation_state else "未設定"
    
    # Excelワークブック作成
    wb = Workbook()
    ws = wb.active
    
    # 申請者名を書き込む
    ws["A3"] = "申請者名"
    ws["B3"] = applicant_name  # ← ここで使用
    
    # ... 残りの処理 ...
    
    wb.save(file_path)
    
    return {
        "success": True,
        "file_path": str(file_path),
        "message": f"申請書を作成しました: {file_path}"
    }
```

---

## トラブルシューティング

### Q1: 申請者名が「未設定」になる

**原因**: invocation_stateが正しく渡されていない

**確認ポイント**:
1. 親エージェントで `agent(query, applicant_name=value)` の形式で渡しているか
2. 子エージェントのツール関数で `@tool(context=True)` を使用しているか
3. 子エージェントが自身のagent()を呼び出す際にinvocation_stateを渡しているか
4. ツールで `tool_context.invocation_state.get("applicant_name")` で取得しているか

### Q2: `tool_context.invocation_state` が None になる

**原因**: invocation_stateが渡されていない

**解決方法**:
```python
# ❌ 間違い
response = agent(query)  # invocation_stateを渡していない

# ✅ 正しい
response = agent(query, applicant_name="山田太郎")  # invocation_stateとして渡す
```

### Q3: 子エージェントのツールで申請者名が取得できない

**原因**: 子エージェントが自身のagent()を呼び出す際にinvocation_stateを渡していない

**確認ポイント**:
```python
@tool(context=True)
def child_agent(query: str, tool_context: ToolContext) -> str:
    agent = _get_child_agent()
    
    # invocation_stateから取得
    applicant_name = tool_context.invocation_state.get("applicant_name")
    
    # ★ここが重要★ 子エージェントを呼び出す際に渡す
    if applicant_name:
        response = agent(query, applicant_name=applicant_name)  # ← これを忘れずに
    else:
        response = agent(query)
    
    return str(response)
```

---

## まとめ

### invocation_state の流れ（3ステップ）

1. **親エージェントで渡す**
   ```python
   self.agent(user_input, applicant_name=self._applicant_name)
   ```

2. **子エージェントで受け取って渡す**
   ```python
   # 受け取る
   applicant_name = tool_context.invocation_state.get("applicant_name")
   # 渡す
   agent(query, applicant_name=applicant_name)
   ```

3. **ツールで利用**
   ```python
   # 取得
   applicant_name = tool_context.invocation_state.get("applicant_name")
   # Excelに書き込み
   ws["B3"] = applicant_name
   ```

### キーポイント

- `agent(query, key=value)` の形式でinvocation_stateを渡す
- `@tool(context=True)` を使用すると `ToolContext` が渡される
- `tool_context.invocation_state.get(key)` で値を取得
- 各レベルで明示的に渡す必要がある（自動継承ではない）
- agent.stateよりもシンプルで、Strandsの設計思想に沿っている
