"""経費精算申請エージェント（AG-002）

経費精算申請書の作成を担当する専門エージェント。
オーケストレーターからAgent as Toolsパターンで呼び出される。
"""
import logging
from strands import Agent, tool, ToolContext
from strands_tools import image_reader
from tools.output_generator import generate_expense_report
from prompt.prompt_specialist_expense import get_expense_system_prompt
from knowledge.expense_policies import get_expense_policies, get_expense_category_policies
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
        deadline: 申請期限基準日（YYYY-MM-DD形式）

    Returns:
        Agent: 経費精算申請エージェントのインスタンス
    """
    cfg = settings.expense
    system_prompt = get_expense_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline_date=deadline,
        expense_policies=get_expense_policies(
            deadline_months=cfg.deadline_months,
            approval_threshold=cfg.approval_threshold,
        ),
        expense_category_policies=get_expense_category_policies(),
    )
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[generate_expense_report, image_reader],
        agent_name="経費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )


@tool(context=True)
def expense_agent(query: str, tool_context: ToolContext) -> str:
    """経費精算申請エージェントツール

    経費精算申請書（Excel）の作成を支援します。
    領収書画像から経費情報を抽出し、申請書を生成します。

    Args:
        query: ユーザーからの入力や質問

    Returns:
        str: エージェントからの応答
    """
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-002",
        deadline_months=settings.expense.deadline_months,
        build_agent=_build_expense_agent,
    )
