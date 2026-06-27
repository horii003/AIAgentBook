"""経費精算申請エージェント

一般経費精算申請の情報収集・領収書解析・カテゴリ判定・期限チェック・申請書生成を担当する
専門エージェント（Agent as Tool）。
"""
import logging

from strands import Agent, tool, ToolContext

from agents.base_agent import create_specialist_agent, invoke_specialist_agent
from config.settings import settings
from prompt.prompt_general_expense import get_general_expense_system_prompt
from tools.output_generator import generate_general_expense_form

_logger = logging.getLogger(__name__)


def _build_general_expense_agent(
    session_id: str,
    applicant_name: str,
    application_date: str,
    deadline: str,
) -> Agent:
    """経費精算申請エージェントのインスタンスを生成する。

    Args:
        session_id: セッションID
        applicant_name: 申請者名
        application_date: 申請日（YYYY-MM-DD形式）
        deadline: 申請期限（YYYY-MM-DD形式）

    Returns:
        構成済みのAgentインスタンス
    """
    cfg = settings.general_expense
    system_prompt = get_general_expense_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline=deadline,
    )
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[generate_general_expense_form],
        agent_id="general_expense_agent",
        agent_name="経費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )


@tool(context=True)
def general_expense_agent(query: str, tool_context: ToolContext) -> str:
    """一般経費精算申請の情報収集・領収書解析・カテゴリ判定・期限チェック・申請書生成を行う。

    Args:
        query: オーケストレーターからの質問・指示

    Returns:
        str: エージェントからの応答
    """
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-003",
        deadline_months=settings.general_expense.deadline_months,
        build_agent=_build_general_expense_agent,
    )
