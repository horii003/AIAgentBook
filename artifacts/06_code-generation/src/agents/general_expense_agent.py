"""経費精算申請エージェント。

経費精算申請の経費情報を収集し、経費精算申請書（Excel）を生成する。
AG-001 から Agent as Tool として呼び出される専門エージェント。
"""
from strands import Agent, ToolContext, tool

from agents.base_agent import create_specialist_agent, invoke_specialist_agent
from config.settings import settings
from knowledge.receipt_policies import get_receipt_policies
from prompt.prompt_general_expense import get_general_expense_system_prompt
from tools.output_generator import generate_general_expense_form


# ============ エージェントの初期化 ============

def _build_general_expense_agent(
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
    cfg = settings.general_expense

    # システムプロンプトを生成
    receipt_policies = get_receipt_policies(
        deadline_months=cfg.deadline_months,
        approval_threshold=cfg.approval_threshold,
    )
    system_prompt = get_general_expense_system_prompt(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline=deadline,
        receipt_policies=receipt_policies,
    )

    # エージェントを生成して返却
    return create_specialist_agent(
        session_id=session_id,
        system_prompt=system_prompt,
        tools=[generate_general_expense_form],
        agent_name="経費精算申請エージェント",
        window_size=cfg.window_size,
        max_iterations=cfg.max_iterations,
        max_attempts=cfg.max_attempts,
        initial_delay=cfg.initial_delay,
        max_delay=cfg.max_delay,
    )


# ============ Agent as Tools ============

@tool(context=True)
def general_expense_agent(query: str, tool_context: ToolContext) -> str:
    """経費精算申請を処理する専門エージェント。
    領収書情報収集・経費区分判断・申請書生成を担当する。

    Args:
        query: AG-001 からの指示・ユーザーの申請内容

    Returns:
        str: 処理結果メッセージ（申請書生成完了・エラーメッセージ等）
    """
    return invoke_specialist_agent(
        query=query,
        tool_context=tool_context,
        agent_id="AG-003",
        deadline_months=settings.general_expense.deadline_months,
        build_agent=_build_general_expense_agent,
    )
