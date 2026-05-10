"""交通費精算申請エージェント

移動情報を収集し交通費を計算して交通費精算申請書を生成する専門エージェント。
オーケストレーターからAgent as Toolsパターンで呼び出される。
"""
import logging
from strands import Agent, tool, ToolContext
from tools.transport_tools import calculate_transport_fare
from tools.output_generator import generate_transport_form
from prompt.prompt_transport import get_transport_system_prompt
from knowledge.transport_policies import get_transport_policies
from config.settings import settings
from agents.base_agent import create_specialist_agent, invoke_specialist_agent

_logger = logging.getLogger(__name__)


def _build_transport_agent(
    session_id: str,
    applicant_name: str,
    application_date: str,
    deadline: str,
) -> Agent:
    """交通費精算申請エージェントのインスタンスを作成するビルド関数。

    Args:
        session_id: セッションID
        applicant_name: 申請者名
        application_date: 申請日（YYYY-MM-DD形式）
        deadline: 申請期限（YYYY-MM-DD形式）

    Returns:
        Agent: 交通費精算申請エージェントのインスタンス
    """
    cfg = settings.transport_agent
    transport_policies = get_transport_policies(
        deadline_months=cfg.deadline_months,
        approval_threshold=cfg.approval_threshold,
    )
    system_prompt = get_transport_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline_date=deadline,
        approval_threshold=cfg.approval_threshold,
        transport_policies=transport_policies,
    )
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[calculate_transport_fare, generate_transport_form],
        agent_name="交通費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )


@tool(context=True)
def transport_agent(query: str, tool_context: ToolContext) -> str:
    """交通費精算申請を処理する。移動情報を収集し、交通費を計算して申請書を生成する。

    Args:
        query: ユーザーからの入力や質問

    Note:
        tool_context は Strands SDK が @tool(context=True) により自動注入する。
        LLM へのツールスキーマには含まれず、LLM が値を指定することもない。

    Returns:
        str: エージェントからの応答
    """
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-002",
        deadline_months=settings.transport_agent.deadline_months,
        build_agent=_build_transport_agent,
    )
