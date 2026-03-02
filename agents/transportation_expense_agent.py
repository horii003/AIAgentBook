"""交通費精算申請エージェント"""
import logging
from strands import Agent, tool, ToolContext
from strands import ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from tools.fare_tools import calculate_fare
from tools.excel_generator import transportation_excel_generator
from session.session_manager import SessionManagerFactory
from handlers.human_approval_hook import HumanApprovalHook
from handlers.error_handler import LoopLimitError, ErrorHandler
from prompt.prompt_transportation_expense import _get_transportation_expense_system_prompt
from handlers.loop_control_hook import LoopControlHook
from strands.types.exceptions import ContextWindowOverflowException, MaxTokensReachedException
from config.model_config import ModelConfig

logger = logging.getLogger(__name__)


#エージェントの初期化
def _get_transportation_expense_agent(session_id: str) -> Agent:
    """
    交通費精算申請エージェントのインスタンスを作成
    
    Args:
        session_id: セッションID（必須）
    
    Returns:
        Agent: 交通費精算申請エージェントのインスタンス
    """
    
    # セッションマネージャーの作成
    session_manager = SessionManagerFactory.create_session_manager(session_id)
    
    # Human-in-the-Loop承認フックの作成
    approval_hook = HumanApprovalHook()
    
    # ループ制御フックの作成
    loop_control_hook = LoopControlHook(
        max_iterations=10,  # 専門エージェントは特定タスクに集中するため標準的な回数
        agent_name="交通費精算申請エージェント"
    )

    # エージェントの初期化
    agent = Agent(
        model=ModelConfig.get_model(),
        system_prompt=_get_transportation_expense_system_prompt(),#別モジュールから取得
        tools=[
            calculate_fare,
            transportation_excel_generator
        ],
        conversation_manager=SlidingWindowConversationManager(
            window_size=20,
            should_truncate_results=True,
            per_turn=False
        ),
        agent_id="transportation_expense_agent",
        name="交通費精算申請エージェント",
        description="ユーザーから移動情報を収集し、交通費を計算して申請書を作成します",
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
def transportation_expense_agent(query: str, tool_context: ToolContext) -> str:
    """
    交通費精算申請ツール
    
    ユーザーから移動情報を一区間ずつ収集し、交通費を計算して申請書を作成します。
    会話履歴を保持して、複数回の呼び出しでも段階的に情報を収集します。
    
    Args:
        query: ユーザーからの入力や質問
    
    Returns:
        str: エージェントからの応答
    """
    # ErrorHandlerの初期化
    _error_handler = ErrorHandler()
    
    # ツール呼び出しをログに記録
    logger.info("transportation_expense_agent ツールが呼び出されました")

    try:
        # invocation_stateは受付エージェント側でバリデーション済み
        state = tool_context.invocation_state
        
        # エージェントインスタンスを作成（session_managerが会話履歴を管理）
        agent = _get_transportation_expense_agent(session_id=state["session_id"])
        
        # invocation_stateを渡してエージェント実行
        invocation_state = {
            "applicant_name": state["applicant_name"],
            "application_date": state["application_date"]
        }
        
        response = agent(query, invocation_state=invocation_state)
        
        return str(response)
    
    except LoopLimitError as e:
        # ループ制限エラー
        logger.warning(f"LoopLimitError が発生しました: {str(e)} | agent: {e.agent_name}")
        return _error_handler.handle_loop_limit_error(e)

    except ContextWindowOverflowException as e:
        # コンテキストウィンドウ超過エラー
        logger.warning(f"ContextWindowOverflowException が発生しました: {str(e)}")
        return _error_handler.handle_context_window_error(e)

    except MaxTokensReachedException as e:
        # 最大トークン数到達エラー
        logger.warning(f"MaxTokensReachedException が発生しました: {str(e)}")
        return _error_handler.handle_max_tokens_error(e)

    except RuntimeError as e:
        # RuntimeError
        logger.error(f"RuntimeError が発生しました: {str(e)[:100]} | query: {query[:50]}", exc_info=True)
        return _error_handler.handle_runtime_error(e)
    
    except Exception as e:
        # 予期しないエラー
        logger.error(f"予期しないエラーが発生しました: {type(e).__name__}: {str(e)[:100]} | query: {query[:50]}", exc_info=True)
        return _error_handler.handle_unexpected_error(e)


