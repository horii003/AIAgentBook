# Human-in-the-Loop承認フック実装ガイド

## 概要

このドキュメントでは、Excel申請書生成前にユーザーの承認を求めるHuman-in-the-Loop機能の実装について説明します。

Strands AgentのHooks機能を使用して、`excel_generator`ツール実行前に人間の承認を求め、承認・修正・キャンセルの3つの選択肢を提供します。

## 実装の目的

Excel申請書を自動生成する前に、以下を実現します：

1. **最終確認**: 申請内容を確認し、承認・修正・キャンセルを選択
2. **修正要望の受付**: 内容に誤りがある場合、修正要望を伝えてエージェントに修正させる
3. **キャンセル対応**: 申請を取りやめる場合、適切に処理を終了
4. **品質保証**: 自動生成される申請書の品質を人間が最終確認

## アーキテクチャ

### Strands Hooks機能の活用

```
エージェント実行フロー:
1. ユーザー入力
2. エージェント処理（情報収集・ルールチェック）
3. excel_generatorツール呼び出し準備
4. ★ BeforeToolCallEvent発火 ← ここでHuman-in-the-Loop
5. ユーザーの選択を待つ
   - 承認 → ツール実行
   - 修正 → ツールキャンセル、修正要望をエージェントに伝達
   - キャンセル → ツールキャンセル、申請終了
6. 結果返却
```

### 実装コンポーネント

#### 1. HumanApprovalHook クラス

**ファイル**: `handlers/human_approval_hook.py`

**主要機能**:
- `BeforeToolCallEvent`をフックして、ツール実行前に介入
- `excel_generator`ツール（`receipt_excel_generator`, `travel_excel_generator`）のみを対象
- 承認コールバックを呼び出してユーザーの判断を取得
- 修正要望またはキャンセルの場合は`event.cancel_tool`を設定

**コールバックインターフェース**:
```python
def approval_callback(tool_name: str, tool_params: dict) -> tuple:
    """
    Args:
        tool_name: ツール名
        tool_params: ツールパラメータ
    
    Returns:
        tuple: (approved: bool, feedback: str)
        - approved: True=承認, False=修正要望またはキャンセル
        - feedback: 修正要望の内容、またはキャンセルの場合は"CANCEL"
    """
```

#### 2. エージェントへの統合

**対象エージェント**:
- `agents/travel_agent.py` - 交通費精算申請エージェント
- `agents/receipt_expense_agent.py` - 経費精算申請エージェント

**統合方法**:
```python
from handlers.human_approval_hook import HumanApprovalHook

# フックの作成
approval_hook = HumanApprovalHook()

# エージェント初期化時にフックを追加
agent = Agent(
    model="...",
    tools=[...],
    hooks=[approval_hook]  # ← フックを追加
)
```

## 使用方法

### デフォルトの承認フロー（コンソール入力）

デフォルトでは、コンソールで対話的に承認を求めます：

```
============================================================
【最終確認】申請書を生成します
============================================================
店舗名: ABC書店
金額: ¥3,500
日付: 2024-01-15
品目: 技術書, ノート
経費区分: 事務用品費
------------------------------------------------------------
1. OK（申請書を生成）
2. 修正したい
3. キャンセル

選択 (1-3): 
```

### カスタム承認コールバックの実装

独自の承認ロジックを実装する場合：

```python
def custom_approval_callback(tool_name: str, tool_params: dict) -> tuple:
    """カスタム承認ロジック"""
    
    # 例: 金額が5000円以上の場合は自動承認しない
    if tool_name == "receipt_excel_generator":
        amount = tool_params.get("amount", 0)
        if amount >= 5000:
            return False, "金額が5000円以上のため、上長の承認が必要です"
    
    # 例: 特定の経路は自動承認
    if tool_name == "travel_excel_generator":
        routes = tool_params.get("routes", [])
        if all(route.get("transport_type") == "train" for route in routes):
            return True, ""  # 電車のみの場合は自動承認
    
    # その他の場合は人間に確認
    return ask_human_approval(tool_name, tool_params)

# カスタムコールバックでフックを作成
approval_hook = HumanApprovalHook(approval_callback=custom_approval_callback)
```

## 動作フロー

### 1. 承認された場合

```
1. エージェントがexcel_generatorツールを呼び出そうとする
2. BeforeToolCallEventが発火
3. HumanApprovalHookが承認を求める
4. ユーザーが「1. OK」を選択
5. ツールが実行される
6. Excel申請書が生成される
7. エージェントが結果を返す
```

**実行例:**
```
システム: 【最終確認】申請書を生成します
         経路数: 1件
         合計金額: ¥200
         選択 (1-3): 
ユーザー: 1
✓ 申請書を生成します...

エージェント: ✅ 申請書の作成が完了しました！
         ファイル名：交通費申請書_20260130_123456.xlsx
```

### 2. 修正要望がある場合

```
1. エージェントがexcel_generatorツールを呼び出そうとする
2. BeforeToolCallEventが発火
3. HumanApprovalHookが承認を求める
4. ユーザーが「2. 修正したい」を選択
5. ユーザーが修正内容を入力
6. event.cancel_toolが設定され、ツール実行がキャンセル
7. 修正要望がエージェントに伝えられる
8. エージェントがユーザーと対話して修正を行う
9. 修正後、再度ツール呼び出しが試みられる
10. 再度承認プロセスが実行される
```

**実行例:**
```
システム: 【最終確認】申請書を生成します
         日付: 2026-01-27
         選択 (1-3): 
ユーザー: 2
システム: 修正内容を入力してください: 
ユーザー: 日付を2026-01-29に修正してください
✓ 修正要望: 日付を2026-01-29に修正してください

エージェント: 承知いたしました。日付を2026-01-29に修正いたします。
         [修正後の内容を表示]

システム: 【最終確認】申請書を生成します
         日付: 2026-01-29
         選択 (1-3): 
ユーザー: 1
✓ 申請書を生成します...

エージェント: ✅ 申請書の作成が完了しました！
```

### 3. キャンセルされた場合

```
1. エージェントがexcel_generatorツールを呼び出そうとする
2. BeforeToolCallEventが発火
3. HumanApprovalHookが承認を求める
4. ユーザーが「3. キャンセル」を選択
5. feedback="CANCEL"が設定される
6. event.cancel_toolにキャンセルメッセージが設定される
7. エージェントにキャンセルが伝えられる
8. エージェントが適切に応答
```

**実行例:**
```
システム: 【最終確認】申請書を生成します
         選択 (1-3): 
ユーザー: 3
✗ キャンセルしました。

エージェント: 承知いたしました。申請をキャンセルいたしました。
         他に申請したい内容があればお申し付けください。
         なければ、これで受付を終了いたします。
```

## 技術的詳細

### Strands Hooks APIの使用

```python
class HumanApprovalHook(HookProvider):
    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        # BeforeToolCallEventにコールバックを登録
        registry.add_callback(BeforeToolCallEvent, self.request_approval)
    
    def request_approval(self, event: BeforeToolCallEvent) -> None:
        # ツール名を取得
        tool_name = event.tool_use["name"]
        
        # 対象ツールのみ処理
        if tool_name not in ["receipt_excel_generator", "travel_excel_generator"]:
            return
        
        # 承認を求める
        approved, feedback = self.approval_callback(tool_name, tool_params)
        
        if not approved:
            # キャンセルまたは修正要望の場合
            if feedback.upper() == "CANCEL":
                # キャンセルメッセージ
                event.cancel_tool = "ユーザーが申請をキャンセルしました。..."
            else:
                # 修正要望メッセージ
                event.cancel_tool = f"ユーザーから修正要望がありました: {feedback}..."
```

### キャンセルと修正要望の区別

キャンセルは特別な修正要望として扱われます：

- **修正要望**: `feedback="具体的な修正内容"`
  - エージェントは修正を行い、再度ツールを実行
  
- **キャンセル**: `feedback="CANCEL"`
  - エージェントは申請を終了し、次の要望を待つ

この設計により、`status: "error"`にならず、LLMが適切に処理できます。

### システムプロンプトの調整

エージェントのシステムプロンプトには以下を追加：

```python
"""
**重要**: すべての情報が揃い、ルールチェックが完了したら、
**ユーザーに最終確認を求めずに**直接excel_generatorツールを実行してください
- システムが自動的に承認プロセスを実行します
- 修正が必要な場合は、システムから指示があります
- ツールの実行結果に「キャンセルしました」というメッセージが含まれている場合は、
  ユーザーの指示に従ってください
"""
```

これにより、エージェントとHookの二重確認を防ぎます。

## テスト

### テストファイル
`tests/test_human_approval_hook.py`

### 実行方法
```bash
python -m pytest tests/test_human_approval_hook.py -v
```

### テストケース
1. フックの初期化
2. カスタムコールバックの設定
3. receipt_excel_generatorの承認
4. receipt_excel_generatorのキャンセル
5. receipt_excel_generatorの修正要望
6. travel_excel_generatorの承認
7. 他のツールはスキップされることの確認

## 拡張可能性

### 1. 承認履歴の記録

```python
class HumanApprovalHook(HookProvider):
    def __init__(self, approval_callback=None, log_file="approval_log.json"):
        self.approval_callback = approval_callback or self._default_approval_callback
        self.log_file = log_file
    
    def request_approval(self, event: BeforeToolCallEvent) -> None:
        # ... 承認処理 ...
        
        # 承認履歴を記録
        self._log_approval(tool_name, tool_params, approved, feedback)
```

### 2. 承認ルールエンジンとの統合

```python
from handlers.approval_rules import ApprovalRuleEngine

def rule_based_approval(tool_name: str, tool_params: dict) -> tuple:
    # ルールエンジンで自動判定
    auto_approved, message = ApprovalRuleEngine.check_approval(tool_params)
    
    if auto_approved:
        return True, ""
    
    # ルールで判定できない場合は人間に確認
    return ask_human_approval(tool_name, tool_params)
```

### 3. 非同期承認（Webhook、メール通知など）

```python
async def async_approval_callback(tool_name: str, tool_params: dict) -> tuple:
    # Webhook経由で承認者に通知
    approval_id = await send_approval_request(tool_name, tool_params)
    
    # 承認待ち
    approved, feedback = await wait_for_approval(approval_id)
    
    return approved, feedback
```

## ベストプラクティス

### 1. シンプルなメッセージ
- キャンセルメッセージはシンプルで明確に
- LLMが理解しやすい表現を使用

### 2. 一貫性のある処理
- 修正要望とキャンセルを同じフローで処理
- `status: "error"`を避ける

### 3. ユーザー体験の最適化
- 確認は1回のみ（エージェントとHookの二重確認を避ける）
- 直感的なUI（1/2/3の選択肢）

### 4. テスト可能な設計
- コールバックを外部から注入可能に
- モックを使用したテストが容易

## まとめ

Strands AgentのHooks機能を活用することで、ツール実行前に人間の判断を介入させるHuman-in-the-Loopパターンを実装しました。

**主な利点**:
- エージェントのコードを変更せずに承認機能を追加
- 柔軟なカスタマイズが可能
- テスト可能な設計
- 他のツールに影響を与えない
- シンプルで理解しやすい実装

**適用範囲**:
- 交通費精算申請エージェント（travel_agent）
- 経費精算申請エージェント（receipt_expense_agent）

この実装により、自動化と人間の監督のバランスを取りながら、安全で信頼性の高い申請書生成プロセスを実現しています。
