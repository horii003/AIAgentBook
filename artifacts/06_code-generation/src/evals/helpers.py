"""評価用共通ヘルパー

既存のエージェントコードを修正せず、評価に必要なユーティリティを提供する。
- ブロッキングフックの自動承認パッチ
- 評価用エージェントファクトリ（テレメトリ trace_attributes 付き）
- ActorSimulator を使った動的マルチターン会話
- StrandsEvalsTelemetry によるスパン自動キャプチャ
"""

import logging
from datetime import datetime

from strands import Agent
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands_evals import ActorSimulator
from strands_evals.telemetry import StrandsEvalsTelemetry

logger = logging.getLogger(__name__)


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

    HumanApprovalHook の approval_callback を自動承認（True, ""）に置き換えることで
    generate_expense_report / generate_transport_report の実行をノンブロッキングにする。

    注意: この関数はモジュールレベルでクラスを書き換えるため、
    他のエージェントモジュールをインポートする **前** に呼び出すこと。
    """
    from handlers.human_approval_hook import HumanApprovalHook

    _original_init = HumanApprovalHook.__init__

    def _patched_init(self, approval_callback=None):
        _original_init(self, approval_callback=lambda *a: (True, ""))

    HumanApprovalHook.__init__ = _patched_init


# ============================================================
# モデル・状態ファクトリ
# ============================================================

def get_model():
    """評価器用のモデルを取得する。"""
    from strands.models import BedrockModel
    return BedrockModel(model_id="jp.anthropic.claude-sonnet-4-5-20250929-v1:0")


def create_invocation_state(session_id: str) -> dict:
    """評価用の InvocationState を作成する。

    Args:
        session_id: テストケース固有のセッションID

    Returns:
        dict: InvocationState の model_dump() 結果
    """
    from models.data_models import InvocationState

    return InvocationState(
        applicant_name="評価テスト 太郎",
        application_date=datetime.now().strftime("%Y-%m-%d"),
        session_id=session_id,
    ).model_dump()


# ============================================================
# エージェントファクトリ
# ============================================================

def create_orchestrator_agent(session_id: str) -> Agent:
    """評価用のオーケストレーターエージェント（AG-001）を作成する。

    本番と同一構成（モデル・システムプロンプト・ツール・ハンドラー）で Agent を直接生成する。
    OrchestratorAgent クラスの input() ループは使用しない。

    Args:
        session_id: セッションID（テレメトリの trace_attributes に設定）

    Returns:
        Agent: 評価用エージェントインスタンス
    """
    from agents.expense_agent import expense_agent
    from agents.transport_agent import transport_agent
    from config.model_config import ModelConfig
    from config.settings import settings
    from handlers.loop_control_hook import LoopControlHook
    from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT

    cfg = settings.orchestrator
    return Agent(
        model=ModelConfig.get_model(),
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        tools=[expense_agent, transport_agent],
        conversation_manager=SlidingWindowConversationManager(
            window_size=cfg.window_size,
            should_truncate_results=True,
            per_turn=False,
        ),
        callback_handler=None,
        hooks=[LoopControlHook(max_iterations=cfg.max_iterations, agent_name="申請受付窓口エージェント")],
        trace_attributes={
            "session.id": session_id,
            "gen_ai.conversation.id": session_id,
        },
    )


# ============================================================
# 会話実行（ActorSimulator ベース）
# ============================================================

def run_actor_conversation(
    agent, case, invocation_state_dict: dict, max_turns: int = 30
) -> list[dict]:
    """ActorSimulator を使ってエージェントと動的マルチターン会話を実行する。

    ActorSimulator が LLM ベースのユーザーシミュレータとして動的に応答を生成し、
    エージェントの応答に基づいて次のユーザー発話を決定する。

    Args:
        agent: strands Agent インスタンス
        case: strands_evals Case オブジェクト
        invocation_state_dict: InvocationState を model_dump() した dict
        max_turns: 最大ターン数（デフォルト: 30）

    Returns:
        list[dict]: 各ターンの {"user_prompt", "agent_response"} リスト
    """
    user_sim = ActorSimulator.from_case_for_user_simulator(
        case=case,
        model=get_model(),
        max_turns=max_turns,
    )
    turns = []
    user_message = case.input

    while user_sim.has_next():
        try:
            memory_exporter.clear()
            result = agent(user_message, invocation_state=invocation_state_dict)
            response = str(result)
            turns.append({"user_prompt": user_message, "agent_response": response})
            logger.info("ターン %d 完了: %s", len(turns), response[:100])
        except Exception as e:
            logger.error("エージェント例外: %s", e)
            break

        try:
            user_result = user_sim.act(response)
            user_message = str(user_result.structured_output.message)
        except Exception as e:
            logger.error("シミュレーター例外: %s", e)
            break

    return turns
