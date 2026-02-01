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
from models.data_models import InvocationState
from pydantic import ValidationError


# グローバル変数
receipt_expense_agent_instance = None
_session_manager = None


def _get_receipt_expense_agent(session_id: str = None) -> Agent:
    """
    経費精算申請エージェントのインスタンスを取得（シングルトンパターン）
    
    Args:
        session_id: セッションID（省略時はセッション管理なし）
    
    Returns:
        Agent: 経費精算申請エージェントのインスタンス
    """
    global receipt_expense_agent_instance, _session_manager
    
    if receipt_expense_agent_instance is None:
        # セッションマネージャーの作成（session_idが指定されている場合）
        if session_id:
            _session_manager = SessionManagerFactory.create_session_manager(session_id)
        
        # Human-in-the-Loop承認フックの作成
        approval_hook = HumanApprovalHook()
        
        # ループ制御フックの作成
        loop_control_hook = LoopControlHook(
            max_iterations=10,  # 専門エージェントは特定タスクに集中するため標準的な回数
            agent_name="経費精算申請エージェント"
        )
        
        # エージェントの初期化
        receipt_expense_agent_instance = Agent(
            model="jp.anthropic.claude-sonnet-4-5-20250929-v1:0",
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
            session_manager=_session_manager,  # セッションマネージャーを設定
            hooks=[approval_hook, loop_control_hook]  # Human-in-the-Loop承認フックとループ制御フックを追加
        )
    
    return receipt_expense_agent_instance

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
        # invocation_stateのバリデーション
        if not tool_context or not tool_context.invocation_state:
            logger.warning("[receipt_expense_agent] invocation_stateが存在しません")
            return "申請者情報が設定されていません。受付窓口に戻ります。"
        
        try:
            state = InvocationState(**tool_context.invocation_state)
        except ValidationError as e:
            logger.error(f"[receipt_expense_agent] invocation_stateのバリデーションエラー: {e}")
            error_messages = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{field}: {error['msg']}")
            return f"申請者情報が不正です: {', '.join(error_messages)}"
        
        # エージェントインスタンスを取得（初回は初期化、2回目以降は既存インスタンスを使用）
        agent = _get_receipt_expense_agent(session_id=state.session_id)
        
        # invocation_stateを渡してエージェント実行
        invocation_state = {
            "applicant_name": state.applicant_name,
            "application_date": state.application_date
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


def reset_receipt_expense_agent():
    """
    経費精算申請エージェントの状態をリセット
    
    新しい申請を開始する際に呼び出すことで、会話履歴をクリアする。
    """
    global receipt_expense_agent_instance, _session_manager
    receipt_expense_agent_instance = None
    _session_manager = None

