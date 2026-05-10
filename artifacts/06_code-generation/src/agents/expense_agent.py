"""経費精算申請エージェント

経費情報を収集し経費区分を判断して経費精算申請書を生成する専門エージェント。
オーケストレーターからAgent as Toolsパターンで呼び出される。
"""
import logging
from strands import Agent, tool, ToolContext
from tools.output_generator import generate_expense_form
from prompt.prompt_expense import get_expense_system_prompt
from knowledge.expense_policies import get_expense_policies
from config.settings import settings
from agents.base_agent import create_specialist_agent, invoke_specialist_agent

_logger = logging.getLogger(__name__)


def _build_expense_agent(
    session_id: str,
    applicant_name: str,
    application_date: str,
    deadline: str,
) -> Agent:
    """経費精算申請エージェントのインスタンスを作成するビルド関数。

    Args:
        session_id: セッションID
        applicant_name: 申請者名
        application_date: 申請日（YYYY-MM-DD形式）
        deadline: 申請期限（YYYY-MM-DD形式）

    Returns:
        Agent: 経費精算申請エージェントのインスタンス
    """
    cfg = settings.expense_agent
    expense_policies = get_expense_policies(
        deadline_months=cfg.deadline_months,
        approval_threshold=cfg.approval_threshold,
    )
    system_prompt = get_expense_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline_date=deadline,
        approval_threshold=cfg.approval_threshold,
        expense_policies=expense_policies,
    )
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[generate_expense_form],
        agent_name="経費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )


@tool(context=True)
def expense_agent(query: str, tool_context: ToolContext) -> str:
    """経費精算申請を処理する。経費情報を収集し、経費区分を判断して申請書を生成する。

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
        agent_id="AG-003",
        deadline_months=settings.expense_agent.deadline_months,
        build_agent=_build_expense_agent,
    )
