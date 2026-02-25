"""評価用共通ヘルパー

既存のエージェントコードを修正せず、評価に必要なユーティリティを提供します。
- HumanApprovalHook の自動承認パッチ
- 評価用エージェントファクトリ（テレメトリ trace_attributes 付き）
- ActorSimulator を使った動的マルチターン会話
- StrandsEvalsTelemetry によるスパン自動キャプチャ
"""

import logging

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
# HumanApprovalHook パッチ
# ============================================================

def patch_human_approval_hook():
    """HumanApprovalHook を自動承認に差し替える。

    既存コードの HumanApprovalHook は input() でコンソール入力を求めるため、
    評価時にブロックされる。approval_callback を自動承認に置き換えることで
    Excel 生成ツールの実行をノンブロッキングにする。

    注意: この関数はモジュールレベルでクラスを書き換えるため、
    他のエージェントモジュールをインポートする **前** に呼び出すこと。
    """
    from handlers.human_approval_hook import HumanApprovalHook

    _original_init = HumanApprovalHook.__init__

    def _auto_approve_init(self, approval_callback=None):
        _original_init(
            self,
            approval_callback=lambda tool_name, tool_params: (True, ""),
        )

    HumanApprovalHook.__init__ = _auto_approve_init
    logger.info("HumanApprovalHook を自動承認モードに差し替えました")


# ============================================================
# モデル・状態ファクトリ
# ============================================================

def get_model():
    """評価器用のモデルを取得する。"""
    from config.model_config import ModelConfig
    return ModelConfig.get_model()


def create_invocation_state(session_id):
    """評価用の InvocationState を作成する。"""
    from datetime import datetime
    from models.data_models import InvocationState
    return InvocationState(
        applicant_name="評価太郎",
        application_date=datetime.now().strftime("%Y-%m-%d"),
        session_id=session_id,
    )


# ============================================================
# エージェントファクトリ
# ============================================================

def create_reception_agent(session_id):
    """評価用の受付エージェントを作成する。

    ReceptionAgent クラスは input() を使うため直接使えない。
    同じ構成（モデル・プロンプト・ツール・フック）で Agent を直接生成する。

    Args:
        session_id: セッションID（テレメトリの trace_attributes に設定）
    """
    from agents.transportation_expense_agent import transportation_expense_agent
    from agents.receipt_expense_agent import receipt_expense_agent
    from config.model_config import ModelConfig
    from prompt.prompt_reception import RECEPTION_SYSTEM_PROMPT
    from handlers.loop_control_hook import LoopControlHook

    return Agent(
        model=ModelConfig.get_model(),
        system_prompt=RECEPTION_SYSTEM_PROMPT,
        tools=[transportation_expense_agent, receipt_expense_agent],
        conversation_manager=SlidingWindowConversationManager(
            window_size=30,
            should_truncate_results=True,
            per_turn=False,
        ),
        callback_handler=None,
        hooks=[LoopControlHook(max_iterations=10, agent_name="eval_reception")],
        trace_attributes={
            "session.id": session_id,
            "gen_ai.conversation.id": session_id,
        },
    )


# ============================================================
# 会話実行（ActorSimulator ベース）
# ============================================================

def run_actor_conversation(agent, case, invocation_state_dict, max_turns=10):
    """ActorSimulator を使ってエージェントと動的マルチターン会話を実行する。

    ActorSimulator が LLM ベースのユーザーシミュレータとして動的に応答を生成し、
    エージェントの応答に基づいて次のユーザー発話を決定する。

    Args:
        agent: strands Agent インスタンス
        case: strands_evals Case オブジェクト
        invocation_state_dict: InvocationState を model_dump() した dict
        max_turns: 最大ターン数（デフォルト: 10）

    Returns:
        list[dict]: 各ターンの {"user_prompt", "agent_response"} リスト
    """
    from config.model_config import ModelConfig

    user_sim = ActorSimulator.from_case_for_user_simulator(
        case=case,
        model=ModelConfig.DEFAULT_MODEL_ID,
        max_turns=max_turns,
    )

    turns = []
    user_message = case.input

    while user_sim.has_next():
        try:
            result = agent(user_message, invocation_state=invocation_state_dict)
            response = str(result)
        except Exception as e:
            logger.error(f"Agent error on message '{user_message[:60]}': {e}")
            response = f"[ERROR] {type(e).__name__}: {e}"

        turns.append({
            "user_prompt": user_message,
            "agent_response": response,
        })
        logger.info(
            "Turn %d: response='%s'",
            len(turns),
            response[:100],
        )

        # シミュレータに応答を渡し、次のユーザーメッセージを生成
        try:
            user_result = user_sim.act(response)
            user_message = str(user_result.structured_output.message)
        except Exception as e:
            logger.error(f"ActorSimulator error: {e}")
            break

    return turns
