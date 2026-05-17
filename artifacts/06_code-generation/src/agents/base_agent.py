"""エージェント共通ユーティリティ

専門エージェントの生成・呼び出しに共通する処理を集約する。
"""

import logging
from typing import Callable

from dateutil.relativedelta import relativedelta
from dateutil import parser as date_parser
from strands import Agent, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager

from config.model_config import ModelConfig
from handlers.error_handler import ErrorHandler, LoopLimitError
from handlers.human_approval_hook import HumanApprovalHook
from handlers.loop_control_hook import LoopControlHook
from session.session_manager import SessionManagerFactory

_logger = logging.getLogger(__name__)


def calculate_deadline(application_date: str, deadline_months: int) -> str:
    """申請日から申請期限基準日を計算する。

    Args:
        application_date: 申請日（YYYY-MM-DD）
        deadline_months: 期限月数

    Returns:
        期限基準日（YYYY-MM-DD形式）。パース失敗時は "要確認"
    """
    try:
        parsed = date_parser.parse(application_date)
        deadline = parsed - relativedelta(months=deadline_months)
        return deadline.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return "要確認"


def create_specialist_agent(
    session_id: str,
    system_prompt: str,
    tools: list,
    agent_name: str,
    window_size: int = 20,
    max_iterations: int = 10,
    max_attempts: int = 6,
    initial_delay: int = 4,
    max_delay: int = 240,
    target_tools: list[str] | None = None,
) -> Agent:
    """専門エージェントを生成する共通ファクトリ。

    Args:
        session_id: セッションID
        system_prompt: システムプロンプト
        tools: ツール関数リスト
        agent_name: エージェント表示名
        window_size: 会話ウィンドウサイズ
        max_iterations: ReActループ最大回数
        max_attempts: リトライ最大試行回数
        initial_delay: リトライ初期遅延（秒）
        max_delay: リトライ最大遅延（秒）
        target_tools: 承認対象ツール名リスト（Noneの場合は承認フックなし）

    Returns:
        Agent インスタンス
    """
    session_manager = SessionManagerFactory.create_session_manager(session_id)
    loop_control_hook = LoopControlHook(
        max_iterations=max_iterations, agent_name=agent_name
    )

    hooks = []
    if target_tools:
        human_approval_hook = HumanApprovalHook(target_tools=target_tools)
        hooks.append(human_approval_hook)
    hooks.append(loop_control_hook)

    return Agent(
        model=ModelConfig.get_model(),
        system_prompt=system_prompt,
        tools=tools,
        agent_id=agent_name.replace(" ", "_").lower(),
        name=agent_name,
        description=f"{agent_name}の処理を実行する",
        conversation_manager=SlidingWindowConversationManager(
            window_size=window_size,
            should_truncate_results=True,
            per_turn=False,
        ),
        callback_handler=None,
        retry_strategy=ModelRetryStrategy(
            max_attempts=max_attempts,
            initial_delay=initial_delay,
            max_delay=max_delay,
        ),
        session_manager=session_manager,
        hooks=hooks,
    )


def invoke_specialist_agent(
    query: str,
    tool_context,
    agent_id: str,
    deadline_months: int,
    build_agent: Callable,
) -> str:
    """専門エージェントを呼び出す共通ラッパー。

    Args:
        query: ユーザーからの質問・指示
        tool_context: ToolContext（invocation_stateを含む）
        agent_id: エージェントID（ログ用）
        deadline_months: 申請期限月数
        build_agent: エージェントビルド関数

    Returns:
        エージェントの応答文字列またはエラーメッセージ
    """
    state = tool_context.invocation_state
    session_id = state.get("session_id", "")
    applicant_name = state.get("applicant_name", "")
    application_date = state.get("application_date", "")
    deadline = calculate_deadline(application_date, deadline_months)

    agent = build_agent(
        session_id=session_id,
        applicant_name=applicant_name,
        application_date=application_date,
        deadline=deadline,
    )

    # 子エージェントにはsession_idを除いた情報のみ伝播
    child_invocation_state = {
        "applicant_name": applicant_name,
        "application_date": application_date,
    }

    try:
        response = agent(query, invocation_state=child_invocation_state)
        return str(response)
    except LoopLimitError as e:
        _logger.warning(
            "ループ制限到達: agent_id=%s, query=%s", agent_id, query[:50]
        )
        return ErrorHandler.handle_loop_limit_error(e)
    except Exception as e:
        _logger.error(
            "%sエラー: %s, query=%s", agent_id, e, query[:50], exc_info=True
        )
        return ErrorHandler.handle_unexpected_error(e)
