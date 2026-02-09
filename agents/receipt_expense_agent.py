"""経費精算申請エージェント"""
from strands import Agent, tool, ToolContext
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_tools import image_reader
from tools.excel_generator import receipt_excel_generator
from session.session_manager import SessionManagerFactory
from handlers.human_approval_hook import HumanApprovalHook
from prompt.prompt_receipt import _get_receipt_expense_system_prompt
from handlers.loop_control_hook import LoopControlHook
from config.model_config import ModelConfig


def _get_receipt_expense_agent(session_id: str) -> Agent:
    """
    経費精算申請エージェントのインスタンスを作成
    
    Args:
        session_id: セッションID（必須）
    
    Returns:
        Agent: 経費精算申請エージェントのインスタンス
    """
    # セッションマネージャーの作成
    session_manager = SessionManagerFactory.create_session_manager(session_id)
    
    # Human-in-the-Loop承認フックの作成
    approval_hook = HumanApprovalHook()
    
    # ループ制御フックの作成
    loop_control_hook = LoopControlHook(
        max_iterations=10,  # 専門エージェントは特定タスクに集中するため標準的な回数
        agent_name="経費精算申請エージェント"
    )
    
    # エージェントの初期化
    agent = Agent(
        model=ModelConfig.get_model(),
        system_prompt=_get_receipt_expense_system_prompt(),#別モジュールから取得
        tools=[
            image_reader,
            receipt_excel_generator
        ],
        conversation_manager=SlidingWindowConversationManager(
            window_size=15,  # 専門エージェントは特定タスクに集中するため小さめ
            should_truncate_results=True,
            per_turn=False
        ),
        agent_id="receipt_expense_agent",
        name="経費精算申請エージェント",
        description="領収書画像から情報を抽出し、Excel形式の経費精算申請書を自動生成します",
        callback_handler=None,  # ストリーミング出力を無効化
        retry_strategy=ModelRetryStrategy(
            max_attempts=6,
            initial_delay=4,
            max_delay=240
        ),
        session_manager=session_manager,  # セッションマネージャーを設定
        hooks=[approval_hook, loop_control_hook]  # Human-in-the-Loop承認フックとループ制御フックを追加
    )
    
    return agent

#Agent as Tools
@tool(context=True)
def receipt_expense_agent(query: str, tool_context: ToolContext) -> str:
    """
    経費精算申請ツール
    
    領収書画像から情報を抽出し、Excel形式の経費精算申請書を自動生成します。
    会話履歴を保持するため、複数回の呼び出しで段階的に情報を収集できます。
    
    Args:
        query: ユーザーからの入力や質問
    
    Returns:
        str: エージェントからの応答
    """
    import logging
    logger = logging.getLogger(__name__)
    logger.info("[receipt_expense_agent] ツールが呼び出されました")

    try:
        # invocation_stateは受付エージェント側でバリデーション済み
        state = tool_context.invocation_state
        
        # エージェントインスタンスを作成（session_managerが会話履歴を管理）
        agent = _get_receipt_expense_agent(session_id=state["session_id"])
        
        # invocation_stateを渡してエージェント実行
        invocation_state = {
            "applicant_name": state["applicant_name"],
            "application_date": state["application_date"]
        }
        
        response = agent(query, invocation_state=invocation_state)
        
        return str(response)
    
    except RuntimeError as e:
        # ループ制限エラーの処理
        if "エージェントループの制限" in str(e):
            return (
                "申し訳ございません。処理が複雑すぎて完了できませんでした。\n\n"
                "以下のいずれかをお試しください：\n"
                "1. 領収書を1枚ずつ申請してください\n"
                "2. より具体的な情報を提供してください\n"
                "3. 不要な情報を削除してください\n\n"
                "受付窓口に戻りますので、もう一度シンプルな内容でお試しください。"
            )
        else:
            return f"エラーが発生しました。受付窓口に戻ります。"
    
    except Exception as e:
        logger.error(f"[receipt_expense_agent] エラーが発生しました: {e}")
        return f"エラーが発生しました。受付窓口に戻ります。"

