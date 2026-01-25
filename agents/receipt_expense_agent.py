"""経費精算申請エージェント"""
from strands import Agent, tool, ToolContext
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_tools import image_reader
from tools.excel_generator import excel_generator


# システムプロンプト
RECEIPT_EXPENSE_SYSTEM_PROMPT = """あなたは経費精算申請エージェントです。

## 役割

1. **領収書画像の処理**
   - image_readerツールで画像から情報を抽出（店舗名、金額、日付、品目）

2. **経費区分の判断**
   - 品目を分析して適切な経費区分を判断：
     * 事務用品費: 書籍、文房具、オフィス用品など
     * 宿泊費: ホテル、宿泊施設など
     * 資格精算費: 資格試験、受験料、認定費用など
     * その他経費: 上記以外

3. **Excel申請書の生成**
   - excel_generatorツールで申請書を生成
   - 金額が30,000円を超える場合はエラーを返す

## 処理フロー
1. ユーザーから領収書画像のパスを収集
2. image_readerツールで画像から情報を抽出
3. 抽出した情報をユーザーに確認
4. 必要に応じて修正を受け付ける
5. excel_generatorツールで申請書を生成・保存

## 重要な注意事項
- 領収書画像のパスは必ず確認してください
- 抽出した情報は必ずユーザーに確認してください
- 金額が30,000円を超える場合はエラーを通知してください
- 申請書の生成が完了したら、ファイルパスを明示してください

常に丁寧で分かりやすい日本語で対話してください。
"""

# グローバル変数
receipt_expense_agent_instance = None


def _get_receipt_expense_agent() -> Agent:
    """
    経費精算申請エージェントのインスタンスを取得（シングルトンパターン）
    
    Returns:
        Agent: 経費精算申請エージェントのインスタンス
    """
    global receipt_expense_agent_instance
    
    if receipt_expense_agent_instance is None:
        # エージェントの初期化
        receipt_expense_agent_instance = Agent(
            model="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
            system_prompt=RECEIPT_EXPENSE_SYSTEM_PROMPT,
            tools=[
                image_reader,
                excel_generator
            ],
            conversation_manager=SlidingWindowConversationManager(),
            agent_id="receipt_expense_agent",
            name="経費精算申請エージェント",
            description="領収書画像から情報を抽出し、Excel形式の経費精算申請書を自動生成します",
            callback_handler=None  # ストリーミング出力を無効化
        )
    
    return receipt_expense_agent_instance

#Agent as Tools
@tool
def receipt_expense_agent(query: str) -> str:
    """
    経費精算申請ツール
    
    領収書画像から情報を抽出し、Excel形式の経費精算申請書を自動生成します。
    会話履歴を保持するため、複数回の呼び出しで段階的に情報を収集できます。
    
    Args:
        query: ユーザーからの入力や質問
    
    Returns:
        str: エージェントからの応答
    """
    try:
        # エージェントインスタンスを取得（初回は初期化、2回目以降は既存インスタンスを使用）
        agent = _get_receipt_expense_agent()
        
        # エージェント実行
        response = agent(query)
        
        return str(response)
    
    except Exception as e:
        return f"エラーが発生しました: {e}"


def reset_receipt_expense_agent():
    """
    経費精算申請エージェントの状態をリセット
    
    新しい申請を開始する際に呼び出すことで、会話履歴をクリアする。
    """
    global receipt_expense_agent_instance
    receipt_expense_agent_instance = None
