"""交通費精算申請エージェント

交通費精算に必要な情報をユーザーとの対話で収集し、
運賃計算・期限チェック・申請書生成を行う専門エージェント。
オーケストレーターからAgent as Toolsパターンで呼び出される。
"""
import logging

from strands import Agent, tool, ToolContext

from agents.base_agent import create_specialist_agent, invoke_specialist_agent
from config.settings import settings
from prompt.prompt_transportation_expense import get_transportation_expense_system_prompt
from tools.transportation_tools import calculate_transportation_cost
from tools.output_generator import generate_transportation_expense_form

_logger = logging.getLogger(__name__)


def _build_transportation_expense_agent(
    session_id: str,
    applicant_name: str,
    application_date: str,
    deadline: str,
) -> Agent:
    """交通費精算申請エージェントのインスタンスを生成する。

    Args:
        session_id: セッションID
        applicant_name: 申請者名
        application_date: 申請日（YYYY-MM-DD形式）
        deadline: 申請期限（YYYY-MM-DD形式）

    Returns:
        構成済みのAgentインスタンス
    """
    cfg = settings.transportation_expense
    system_prompt = get_transportation_expense_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline=deadline,
    )
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[calculate_transportation_cost, generate_transportation_expense_form],
        agent_id="transportation_expense_agent",
        agent_name="交通費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )


@tool(context=True)
def transportation_expense_agent(query: str, tool_context: ToolContext) -> str:
    """交通費精算申請を処理する専門エージェント。

    ユーザーとの対話を通じて交通費精算に必要な情報を収集し、
    運賃計算・申請期限チェック・申請書生成を行う。

    Args:
        query: オーケストレーターからの質問・指示テキスト

    Returns:
        str: エージェントからの応答
    """
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-002",
        deadline_months=settings.transportation_expense.deadline_months,
        build_agent=_build_transportation_expense_agent,
    )
