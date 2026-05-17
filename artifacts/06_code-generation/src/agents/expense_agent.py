"""経費精算申請エージェント（AG-002）

経費精算申請書の作成を支援する専門エージェント。
"""

from strands import Agent, ToolContext, tool

from agents.base_agent import create_specialist_agent, invoke_specialist_agent
from config.settings import settings
from prompt.prompt_expense import get_expense_system_prompt
from tools.output_generator import generate_expense_report


def _build_expense_agent(
    session_id: str, applicant_name: str, application_date: str, deadline: str
) -> Agent:
    """経費精算申請エージェントを生成する"""
    system_prompt = get_expense_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline_date=deadline,
    )
    cfg = settings.expense
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[generate_expense_report],
        agent_name="経費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
        target_tools=["generate_expense_report"],
    )


@tool(context=True)
def expense_agent(query: str, tool_context: ToolContext) -> str:
    """経費精算申請の処理を実行する。

    Args:
        query: ユーザーからの経費精算に関する質問・指示
    """
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-002",
        deadline_months=settings.expense.deadline_months,
        build_agent=_build_expense_agent,
    )
