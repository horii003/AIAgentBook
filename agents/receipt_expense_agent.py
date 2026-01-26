"""経費精算申請エージェント"""
from strands import Agent, tool, ToolContext
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_tools import image_reader
from tools.excel_generator import receipt_excel_generator
from handlers.steering_handler import LoggedSteeringHandler, steering_logger


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
   - receipt_excel_generatorツールで申請書を生成
   - 金額が30,000円を超える場合はエラーを返す

## 処理フロー
1. ユーザーから領収書画像のパスを収集
2. image_readerツールで画像から情報を抽出
3. 抽出した情報をユーザーに確認
4. 必要に応じて修正を受け付ける
5. receipt_excel_generatorツールで申請書を生成・保存

## 重要な注意事項
- 領収書画像のパスは必ず確認してください
- 抽出した情報は必ずユーザーに確認してください
- 金額が30,000円を超える場合はエラーを通知してください
- 申請書の生成が完了したら、ファイルパスを明示してください

ルール検証との連携:
- 申請内容はルール検証エージェントによって自動的にチェックされます
- 検証結果に基づいて適切に対応してください：
  * "proceed": そのまま処理を続行
  * "guide": 提案された修正をユーザーに確認
  * "interrupt": 処理を一時停止し、ユーザーに詳細確認を求める
 
常に丁寧で分かりやすい日本語で対話してください。
"""
# 検証ルール
rule_steering = LoggedSteeringHandler(
    system_prompt="""あなたは交通費精算のルール検証エージェントです。
メインエージェントの申請内容を検証し、適切なガイダンスを提供してください。

あなたの役割:
メインエージェントが交通費申請を処理する際に、コンテキストに応じたガイダンスを提供します。
ただし、image_readerツール利用時は検証は実施しません。

申請ルール:
１．日付：過去3か月を超える場合は修正提案をし、直らなければユーザーの確認を求める
２．5000円を超える申請は事前に上長承認しているかをユーザーに確認する
３．目的が業務関連か確認し、業務目的と判断できない場合は、ユーザーに詳細な目的確認を求める

判断基準と応答:
- ルール準拠 → "proceed": 処理を続行してよい
- 軽微な違反 → "guide": メインエージェントに修正提案を促す具体的なガイダンスを提供
- 重大な違反 → "interrupt": 人間の確認が必要（注意：interruptは実際にエージェントを停止させます）

重要: interruptを使用する場合の条件
- 5000円を超える申請で上長承認の確認が取れていない場合
- 業務目的が不明確で高額（5000円以上）の申請の場合
- 過去3か月を超える日付で業務上の正当な理由が不明な場合

応答形式:
判断結果と理由を明確に示してください。
例：
- "proceed: すべてのルールに準拠しています"
- "guide: 日付が3か月以上前です。ユーザーに確認を求めてください"
- "interrupt: 業務目的が不明確で、高額（10000円）です。上長の承認確認が必要です"
"""
)

# グローバル変数
receipt_expense_agent_instance = None
receipt_expense_agent_interrupt_state = None  # interrupt状態を保持


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
                receipt_excel_generator
            ],
            hooks=[rule_steering],
            conversation_manager=SlidingWindowConversationManager(),
            agent_id="receipt_expense_agent",
            name="経費精算申請エージェント",
            description="領収書画像から情報を抽出し、Excel形式の経費精算申請書を自動生成します",
            callback_handler=None,  # ストリーミング出力を無効化
            retry_strategy=ModelRetryStrategy(
                max_attempts=6,
                initial_delay=4,
                max_delay=240
            )
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

    global receipt_expense_agent_interrupt_state

    try:
        steering_logger.info(f"Receipt expense agent called: {query[:100]}...")

        # エージェントインスタンスを取得（初回は初期化、2回目以降は既存インスタンスを使用）
        agent = _get_receipt_expense_agent()
        
        # interrupt再開処理
        if receipt_expense_agent_interrupt_state is not None:
            steering_logger.info("Resuming from interrupt...")
            
            # ユーザーの応答を解析
            user_response = query.lower().strip()
            approval = "y" if user_response in ["承認", "y", "yes", "はい", "ok"] else "n"
            
            # interruptResponseを作成
            interrupt_responses = []
            for interrupt in receipt_expense_agent_interrupt_state.interrupts:
                interrupt_responses.append({
                    "interruptResponse": {
                        "interruptId": interrupt.id,
                        "response": approval
                    }
                })
            
            # interrupt状態をクリア
            receipt_expense_agent_interrupt_state = None
            
            # エージェントを再開
            response = agent(interrupt_responses)
        else:
            # 通常の実行
            response = agent(query)

        # interrupt処理
        if response.stop_reason == "interrupt":
            steering_logger.warning(f"Agent interrupted: {len(response.interrupts)} interrupt(s)")
            
            # interrupt状態を保存
            receipt_expense_agent_interrupt_state = response
            
            # interrupt情報を整形して返す
            interrupt_messages = []
            for interrupt in response.interrupts:
                reason = interrupt.reason if hasattr(interrupt, 'reason') else "確認が必要です"
                interrupt_messages.append(f"[重要な確認] {reason}")
            
            return "\n".join(interrupt_messages) + "\n\n上記の確認が必要です。承認する場合は「承認」または「y」、拒否する場合は「拒否」または「n」と入力してください。"
        
        steering_logger.info("Reciept expense agent response generated")
                
        return str(response)
    
    except Exception as e:
        steering_logger.error(f"Reciept expense  agent error: {str(e)}")
        # エラー時はinterrupt状態をクリア
        receipt_expense_agent_interrupt_state = None
        return f"エラーが発生しました: {e}"


def reset_receipt_expense_agent():
    """
    経費精算申請エージェントの状態をリセット
    
    新しい申請を開始する際に呼び出すことで、会話履歴をクリアする。
    """
    global receipt_expense_agent_instance
    receipt_expense_agent_instance = None
    receipt_expense_agent_interrupt_state = None

