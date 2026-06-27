"""エージェント共通ユーティリティ

全専門エージェントで共有するヘルパー関数・定数を定義する。
"""
import logging
from datetime import datetime
from typing import Callable

from dateutil.relativedelta import relativedelta
from strands import Agent, ToolContext, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager

from handlers.error_handler import LoopLimitError, ErrorHandler
from handlers.human_approval_hook import HumanApprovalHook
from handlers.loop_control_hook import LoopControlHook
from session.session_manager import SessionManagerFactory
from config.model_config import ModelConfig

_logger = logging.getLogger(__name__)

# HumanApprovalHookの対象ツール
_APPROVAL_TARGET_TOOLS = [
    "generate_transportation_expense_form",
    "generate_general_expense_form",
]


def calculate_deadline(application_date: str, deadline_months: int) -> str:
    """申請日から申請期限を計算して返す。

    Args:
        application_date: 申請日（YYYY-MM-DD形式）
        deadline_months: 申請期限（経費発生日からの月数）

    Returns:
        str: 申請期限（YYYY-MM-DD形式）。パース失敗時は "要確認"。
    """
    try:
        app_dt = datetime.strptime(application_date, "%Y-%m-%d")
        deadline_dt = app_dt - relativedelta(months=deadline_months)
        return deadline_dt.strftime("%Y-%m-%d")
    except Exception:
        _logger.warning(
            "申請期限の計算に失敗しました。申請期限チェックが無効化されます: "
            "application_date=%r, deadline_months=%d",
            application_date,
            deadline_months,
        )
        return "要確認"


def create_specialist_agent(
    session_id: str,
    system_prompt: str,
    tools: list,
    agent_id: str,
    agent_name: str,
    window_size: int,
    max_iterations: int,
    max_attempts: int,
    initial_delay: int,
    max_delay: int,
) -> Agent:
    """専門エージェントの共通ファクトリー関数。

    Session/HumanApprovalHook/LoopControlHook の生成と Agent インスタンスの
    組み立てを共通化する。各専門エージェントのビルド関数はこれを呼び出す。

    Args:
        session_id: セッションID
        system_prompt: エージェント固有のシステムプロンプト
        tools: エージェント固有のツールリスト
        agent_id: エージェントの一意識別子（snake_case）
        agent_name: エージェント表示名（日本語、ログ表示用）
        window_size: SlidingWindowConversationManager のウィンドウサイズ
        max_iterations: LoopControlHook の最大ループ回数
        max_attempts: ModelRetryStrategy のリトライ回数
        initial_delay: ModelRetryStrategy の初期遅延（秒）
        max_delay: ModelRetryStrategy の最大遅延（秒）

    Returns:
        Agent: 設定済みの Agent インスタンス
    """
    session_manager = SessionManagerFactory.create(session_id)
    approval_hook = HumanApprovalHook(target_tools=_APPROVAL_TARGET_TOOLS)
    loop_hook = LoopControlHook(max_iterations=max_iterations, agent_name=agent_name)

    return Agent(
        model=ModelConfig.get_model(),
        system_prompt=system_prompt,
        callback_handler=None,
        tools=tools,
        agent_id=agent_id,
        name=agent_name,
        description=agent_name,
        conversation_manager=SlidingWindowConversationManager(
            window_size=window_size,
            should_truncate_results=True,
            per_turn=False,
        ),
        retry_strategy=ModelRetryStrategy(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
        ),
        hooks=[approval_hook, loop_hook],
        session_manager=session_manager,
    )


def invoke_specialist_agent(
    query: str,
    tool_context: ToolContext,
    agent_id: str,
    deadline_months: int,
    build_agent: Callable[[str, str, str, str], Agent],
) -> str:
    """専門エージェントの共通呼び出しラッパー。

    invocation_state の取得・deadline 計算・Agent 呼び出し・例外処理を共通化する。
    各専門エージェントのツール関数はこれを呼び出す。

    Args:
        query: ユーザーからの入力
        tool_context: Strands SDK が注入する ToolContext
        agent_id: ログ用エージェントID（例: "AG-002"）
        deadline_months: 申請期限の月数（settings.*.deadline_months）
        build_agent: (session_id, applicant_name, application_date, deadline) -> Agent を返すコールバック

    Returns:
        str: エージェントからの応答
    """
    state = tool_context.invocation_state
    applicant_name = state.get("applicant_name", "")
    application_date = state.get("application_date", "")
    session_id = state.get("session_id", "")

    _logger.info("%s エージェントを開始します: session_id=%s", agent_id, session_id)

    deadline = calculate_deadline(application_date, deadline_months)

    agent = build_agent(session_id, applicant_name, application_date, deadline)

    # session_id は除外して子エージェントに伝播
    child_invocation_state = {
        "applicant_name": applicant_name,
        "application_date": application_date,
    }

    try:
        response = agent(query, invocation_state=child_invocation_state)
        _logger.info("%s エージェントが完了しました", agent_id)
        return str(response)
    except LoopLimitError as e:
        _logger.warning("LoopLimitError: agent_id=%s, query=%s", agent_id, query[:50])
        return ErrorHandler.handle_loop_limit_error(e)
    except Exception as e:
        _logger.error("予期しないエラー: agent_id=%s, query=%s", agent_id, query[:50], exc_info=True)
        return ErrorHandler.handle_unexpected_error(e)
