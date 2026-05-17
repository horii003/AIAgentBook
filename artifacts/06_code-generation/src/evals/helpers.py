"""評価テスト共通ヘルパー

評価スクリプトで共通して使用するユーティリティ関数を提供する。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from unittest.mock import patch

from strands.models.bedrock import BedrockModel
from strands_evals.telemetry import StrandsEvalsTelemetry

from agents.orchestrator_agent import OrchestratorAgent
from config.model_config import ModelConfig
from session.session_manager import SessionManagerFactory

# テレメトリ設定
_telemetry = StrandsEvalsTelemetry()
memory_exporter = _telemetry.memory_exporter


def get_model() -> BedrockModel:
    """評価用モデルを取得する"""
    return ModelConfig.get_model()


def patch_human_approval_hook():
    """HumanApprovalHook を自動承認に差し替える（評価時はユーザー入力不要）"""
    from handlers.human_approval_hook import HumanApprovalHook

    original_init = HumanApprovalHook.__init__

    def patched_init(self, target_tools, approval_callback=None):
        original_init(
            self,
            target_tools=target_tools,
            approval_callback=lambda tool_name, tool_params: (True, ""),
        )

    HumanApprovalHook.__init__ = patched_init


def create_orchestrator_agent(session_id: str) -> OrchestratorAgent:
    """評価用オーケストレーターエージェントを生成する"""
    agent = OrchestratorAgent(applicant_name="評価テストユーザー")
    return agent


def create_invocation_state(session_id: str) -> dict:
    """評価用 invocation_state を生成する"""
    from datetime import datetime

    return {
        "applicant_name": "評価テストユーザー",
        "application_date": datetime.now().strftime("%Y-%m-%d"),
        "session_id": session_id,
    }


def run_actor_conversation(agent, case, invocation_state: dict) -> list[dict]:
    """ActorSimulator による動的会話を実行する（マルチターン評価用）"""
    turns = []
    response = agent._agent(case.input, invocation_state=invocation_state)
    turns.append({"user_input": case.input, "agent_response": str(response)})
    return turns
