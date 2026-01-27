"""交通費精算申請エージェント"""
from strands import Agent, tool, ToolContext
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from tools.fare_tools import load_fare_data, calculate_fare
from tools.excel_generator import travel_excel_generator
from handlers.steering_handler import LoggedSteeringHandler, steering_logger


# システムプロンプト
TRAVEL_SYSTEM_PROMPT = """あなたは交通費精算申請エージェントです。
ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。

処理フロー:
1. ユーザーから一区間の移動情報（出発地、目的地、日付、交通手段）を収集
2. calculate_fareツールで交通費を計算
3. 計算結果をユーザーに確認
4. 次の区間の有無を確認
5. すべての区間の入力完了後、最終確認
6. travel_excel_generatorツールで申請書を生成・保存

重要な注意事項:
- 必ず一区間ずつ処理してください
- 各区間の情報を収集する際は、出発地、目的地、日付、交通手段のすべてを確認してください
- 交通手段は「train」「bus」「taxi」「airplane」のいずれかです
- 計算結果は必ずユーザーに確認してください
- すべての区間の入力が完了したら、最終確認を行ってください

travel_excel_generatorツールの使用方法:
- routesパラメータ: 収集した全経路データのリスト（必須）
- 申請者名は自動的に取得されます（引数として渡す必要はありません）
- ツールは1回だけ呼び出してください
- エラーが発生した場合は、ツールの戻り値のmessageフィールドを確認してください
- successフィールドがtrueの場合のみ成功です

常に丁寧で分かりやすい日本語で対話してください。
"""

# 検証ルール（ログ機能付き）
rule_steering = LoggedSteeringHandler(
    system_prompt="""あなたは交通費精算のルール検証エージェントです。
メインエージェントの申請内容を検証し、適切なガイダンスを提供してください。

あなたの役割:
メインエージェントが交通費申請を処理する際に、コンテキストに応じたガイダンスを提供します。

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
travel_agent_instance = None
travel_agent_interrupt_state = None  # interrupt状態を保持


#エージェントの初期化
def _get_travel_agent() -> Agent:
    """
    交通費精算申請エージェントのインスタンスを取得（シングルトンパターン）
    
    Returns:
        Agent: 交通費精算申請エージェントのインスタンス
    """

    global travel_agent_instance
    
    if travel_agent_instance is None:
        # 運賃データの事前読み込み
        try:
            load_fare_data()
        except Exception as e:
            raise RuntimeError(f"運賃データの読み込みに失敗しました: {e}")
        
        # エージェントの初期化
        travel_agent_instance = Agent(
            model="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
            system_prompt=TRAVEL_SYSTEM_PROMPT,
            tools=[
                calculate_fare,
                travel_excel_generator
            ],
            hooks=[rule_steering],
            conversation_manager=SlidingWindowConversationManager(
                window_size=20,  # 複数区間の情報を保持する必要があるため中程度
                should_truncate_results=True,
                per_turn=False
            ),
            agent_id="travel_agent",
            name="交通費精算申請エージェント",
            description="ユーザーから移動情報を収集し、交通費を計算して申請書を作成します",
            callback_handler=None,  # ストリーミング出力を無効化
            retry_strategy=ModelRetryStrategy(
                max_attempts=6,
                initial_delay=4,
                max_delay=240
            )
        )
    
    return travel_agent_instance

#Agent as Tools
@tool(context=True)
def travel_agent(query: str, tool_context: ToolContext) -> str:
    """
    交通費精算申請ツール
    
    ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。
    会話履歴を保持して、複数回の呼び出しでも段階的に情報を収集します。
    
    Args:
        query: ユーザーからの入力や質問
    
    Returns:
        str: エージェントからの応答
    """
    global travel_agent_interrupt_state
    
    try:
        steering_logger.info(f"Travel agent called: {query[:100]}...")
        
        # エージェントインスタンスを取得（初回は初期化、2回目以降は既存インスタンスを使用する）
        agent = _get_travel_agent()
        
        # invocation_stateから申請者名を取得
        applicant_name = None
        if tool_context and tool_context.invocation_state:
            applicant_name = tool_context.invocation_state.get("applicant_name")
        
        
        # interrupt再開処理
        if travel_agent_interrupt_state is not None:
            steering_logger.info("Resuming from interrupt...")
            
            # ユーザーの応答を解析
            user_response = query.lower().strip()
            approval = "y" if user_response in ["承認", "y", "yes", "はい", "ok"] else "n"
            
            # interruptResponseを作成
            interrupt_responses = []
            for interrupt in travel_agent_interrupt_state.interrupts:
                interrupt_responses.append({
                    "interruptResponse": {
                        "interruptId": interrupt.id,
                        "response": approval
                    }
                })
            
            # interrupt状態をクリア
            travel_agent_interrupt_state = None
            
            # エージェントを再開（invocation_stateを渡す）
            if applicant_name:
                response = agent(interrupt_responses, applicant_name=applicant_name)
            else:
                response = agent(interrupt_responses)
        else:
            # 通常の実行（invocation_stateを渡す）
            if applicant_name:
                response = agent(query, applicant_name=applicant_name)
            else:
                response = agent(query)
        
        # interrupt処理
        if response.stop_reason == "interrupt":
            steering_logger.warning(f"Agent interrupted: {len(response.interrupts)} interrupt(s)")
            
            # interrupt状態を保存
            travel_agent_interrupt_state = response
            
            # interrupt情報を整形して返す
            interrupt_messages = []
            for interrupt in response.interrupts:
                reason = interrupt.reason if hasattr(interrupt, 'reason') else "確認が必要です"
                interrupt_messages.append(f"[重要な確認] {reason}")
            
            return "\n".join(interrupt_messages) + "\n\n上記の確認が必要です。承認する場合は「承認」または「y」、拒否する場合は「拒否」または「n」と入力してください。"
        
        steering_logger.info("Travel agent response generated")
        
        return str(response)
    
    except Exception as e:
        steering_logger.error(f"Travel agent error: {str(e)}")
        # エラー時はinterrupt状態をクリア
        travel_agent_interrupt_state = None
        return f"エラーが発生しました: {e}"


#エージェントのリセット
def reset_travel_agent():
    """
    交通費精算申請エージェントの状態をリセット
    
    ユーザーから会話をリセットしたい要望があった場合は、会話履歴をクリアする。
    """
    global travel_agent_instance, travel_agent_interrupt_state
    travel_agent_instance = None
    travel_agent_interrupt_state = None

