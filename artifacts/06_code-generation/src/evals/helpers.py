"""評価テスト共通ヘルパー

評価スクリプトで共通利用するユーティリティ関数を提供する。
"""
import os
import sys
from datetime import datetime
from unittest.mock import patch
from strands.models import BedrockModel
from strands_evals import Case
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from strands_evals.telemetry import StrandsEvalsTelemetry

# テレメトリの初期化
memory_exporter = InMemorySpanExporter()
StrandsEvalsTelemetry(exporter=memory_exporter)


def get_model() -> BedrockModel:
    """評価用BedrockModelを取得する。

    Returns:
        BedrockModel: 設定済みのBedrockModelインスタンス
    """
    from config.model_config import ModelConfig
    return ModelConfig.get_model()


def create_invocation_state(session_id: str):
    """評価用invocation_stateを作成する。

    Args:
        session_id: セッションID

    Returns:
        dict: invocation_state辞書
    """
    from datetime import datetime

    class InvocationState:
        def __init__(self, session_id):
            self.applicant_name = "評価テストユーザー"
            self.application_date = datetime.now().strftime("%Y-%m-%d")
            self.session_id = session_id

        def model_dump(self):
            return {
                "applicant_name": self.applicant_name,
                "application_date": self.application_date,
                "session_id": self.session_id,
            }

    return InvocationState(session_id)


def create_orchestrator_agent(session_id: str):
    """評価用オーケストレーターエージェントを作成する。

    Args:
        session_id: セッションID

    Returns:
        Agent: オーケストレーターエージェントインスタンス
    """
    from agents.orchestrator_agent import OrchestratorAgent
    agent = OrchestratorAgent(session_id=session_id)
    agent._user_name = "評価テストユーザー"
    agent._build_agent()
    return agent.agent


def patch_human_approval_hook():
    """HumanApprovalHookを自動承認モックに差し替える。

    評価テスト実行時にユーザー入力を不要にするため、
    承認コールバックを常にOKを返す関数に差し替える。
    """
    import handlers.human_approval_hook as hah
    original_init = hah.HumanApprovalHook.__init__

    def patched_init(self, target_tools, approval_callback=None):
        # 常にOKを返すコールバックに差し替える
        auto_approve = lambda tool_name, tool_params: (True, "")
        original_init(self, target_tools, approval_callback=auto_approve)

    hah.HumanApprovalHook.__init__ = patched_init


def run_actor_conversation(agent, case: Case, invocation_state: dict) -> list[dict]:
    """ActorSimulatorによる動的会話を実行する。

    Args:
        agent: 評価対象エージェント
        case: テストケース
        invocation_state: invocation_state辞書

    Returns:
        list[dict]: 会話ターンのリスト（各要素: {"user_input": str, "agent_response": str}）
    """
    turns = []
    # 初回入力でエージェントを呼び出す
    response = agent(case.input, invocation_state=invocation_state)
    turns.append({
        "user_input": case.input,
        "agent_response": str(response),
    })
    return turns
