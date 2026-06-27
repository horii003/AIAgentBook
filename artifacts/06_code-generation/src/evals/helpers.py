"""評価用共通ヘルパー

既存のエージェントコードを修正せず、評価に必要なユーティリティを提供する。
- ブロッキングフックの自動承認パッチ
- 評価用エージェントファクトリ（テレメトリ trace_attributes 付き）
- ActorSimulator を使った動的マルチターン会話
- StrandsEvalsTelemetry によるスパン自動キャプチャ
"""

import logging
import sys
import os
from datetime import datetime

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_evals import ActorSimulator
from strands_evals.telemetry import StrandsEvalsTelemetry

logger = logging.getLogger(__name__)

# src/ をパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ============================================================
# テレメトリ初期化（モジュールレベルシングルトン）
# ============================================================

telemetry = StrandsEvalsTelemetry().setup_in_memory_exporter()
memory_exporter = telemetry.in_memory_exporter


# ============================================================
# ブロッキングフック パッチ
# ============================================================

def patch_human_approval_hook():
    """ブロッキングフックを自動承認に差し替える。

    既存コードのフックは input() でコンソール入力を求めるため、
    評価時にブロックされる。approval_callback を自動承認に置き換えることで
    ツールの実行をノンブロッキングにする。

    注意: この関数はモジュールレベルでクラスを書き換えるため、
    他のエージェントモジュールをインポートする **前** に呼び出すこと。
    """
    from handlers.human_approval_hook import HumanApprovalHook

    _original_init = HumanApprovalHook.__init__

    def _patched_init(self, target_tools=None, approval_callback=None):
        # 自動承認コールバックを注入
        _original_init(
            self,
            target_tools=target_tools or [],
            approval_callback=lambda tool_name, tool_params: (True, ""),
        )

    HumanApprovalHook.__init__ = _patched_init
    logger.info("HumanApprovalHook を自動承認モードにパッチしました")


# ============================================================
# モデル・状態ファクトリ
# ============================================================

def get_model():
    """評価器用のモデルを取得する。

    Returns:
        BedrockModel: エージェント本体と同一構成のモデルインスタンス
    """
    from config.model_config import ModelConfig
    return ModelConfig.get_model()


def create_invocation_state(session_id: str) -> dict:
    """評価用の invocation_state 辞書を作成する。

    Args:
        session_id: テストケース固有のセッションID

    Returns:
        dict: invocation_state として渡す辞書
    """
    return {
        "applicant_name": "評価テストユーザー",
        "application_date": datetime.now().strftime("%Y-%m-%d"),
        "session_id": session_id,
    }


# ============================================================
# エージェントファクトリ
# ============================================================

def create_eval_agent(session_id: str) -> Agent:
    """評価用のオーケストレーターエージェントを作成する。

    既存の OrchestratorAgent クラスは input() ループを持つため直接使えない。
    同じ構成（モデル・プロンプト・ツール・フック）で Agent を直接生成する。

    Args:
        session_id: セッションID（テレメトリの trace_attributes に設定）

    Returns:
        Agent: 評価用のAgentインスタンス
    """
    from agents.transportation_expense_agent import transportation_expense_agent
    from agents.general_expense_agent import general_expense_agent
    from config.model_config import ModelConfig
    from config.settings import settings
    from handlers.loop_control_hook import LoopControlHook
    from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
    from session.session_manager import SessionManagerFactory

    cfg = settings.orchestrator
    session_manager = SessionManagerFactory.create(session_id)
    loop_hook = LoopControlHook(
        max_iterations=cfg.max_iterations,
        agent_name="申請受付窓口エージェント（評価）",
    )

    return Agent(
        model=ModelConfig.get_model(),
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        tools=[transportation_expense_agent, general_expense_agent],
        agent_id="orchestrator_agent_eval",
        name="申請受付窓口エージェント（評価）",
        description="評価用オーケストレーターエージェント",
        conversation_manager=SlidingWindowConversationManager(
            window_size=cfg.window_size,
            should_truncate_results=True,
            per_turn=False,
        ),
        callback_handler=None,
        hooks=[loop_hook],
        session_manager=session_manager,
        trace_attributes={
            "session.id": session_id,
            "gen_ai.conversation.id": session_id,
        },
    )


# ============================================================
# 会話実行（ActorSimulator ベース）
# ============================================================

def run_actor_conversation(
    agent: Agent,
    case,
    invocation_state_dict: dict,
    max_turns: int = 10,
) -> str:
    """ActorSimulator を使ってエージェントと動的マルチターン会話を実行する。

    ActorSimulator が LLM ベースのユーザーシミュレータとして動的に応答を生成し、
    エージェントの応答に基づいて次のユーザー発話を決定する。

    Args:
        agent: strands Agent インスタンス
        case: strands_evals Case オブジェクト
        invocation_state_dict: invocation_state として渡す辞書
        max_turns: 最大ターン数

    Returns:
        str: エージェントの最終応答テキスト

    Note:
        会話ループ内で memory_exporter.clear() を呼んではならない。
        全ターンのスパンを蓄積し、ループ完了後にまとめて Session を構築する。
    """
    user_sim = ActorSimulator.from_case_for_user_simulator(
        case=case,
        model=get_model(),
        max_turns=max_turns,
    )

    user_message = case.input
    agent_response = ""

    while user_sim.has_next():
        # memory_exporter.clear() は呼ばない — 全ターンのスパンを蓄積する
        result = agent(user_message, invocation_state=invocation_state_dict)
        agent_response = str(result)

        user_result = user_sim.act(agent_response)
        user_message = str(user_result.structured_output.message)

    return agent_response
