"""交通費精算申請エージェント（AG-003）

交通費精算申請書の作成を支援する専門エージェント。
"""

from strands import Agent, ToolContext, tool

from agents.base_agent import create_specialist_agent, invoke_specialist_agent
from config.settings import settings
from prompt.prompt_transport import get_transport_system_prompt
from tools.output_generator import generate_transport_report
from tools.transport_tools import calculate_transport_fare


def _build_transport_agent(
    session_id: str, applicant_name: str, application_date: str, deadline: str
) -> Agent:
    """交通費精算申請エージェントを生成する"""
    system_prompt = get_transport_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline_date=deadline,
    )
    cfg = settings.transport
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[calculate_transport_fare, generate_transport_report],
        agent_name="交通費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
        target_tools=["generate_transport_report"],
    )


@tool(context=True)
def transport_agent(query: str, tool_context: ToolContext) -> str:
    """交通費精算申請の処理を実行する。

    Args:
        query: ユーザーからの交通費精算に関する質問・指示
    """
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-003",
        deadline_months=settings.transport.deadline_months,
        build_agent=_build_transport_agent,
    )
