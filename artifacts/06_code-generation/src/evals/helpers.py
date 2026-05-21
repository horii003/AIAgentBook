"""評価用共通ヘルパー

既存のエージェントコードを修正せず、評価に必要なユーティリティを提供する。
- ブロッキングフックの自動承認パッチ
- 評価用エージェントファクトリ（テレメトリ trace_attributes 付き）
- ActorSimulator を使った動的マルチターン会話
- StrandsEvalsTelemetry によるスパン自動キャプチャ
"""

import logging
from datetime import datetime

from strands import Agent, ModelRetryStrategy
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

    既存コードのフックは input() でコンソール入力を求めるため、
    評価時にブロックされる。approval_callback を自動承認に置き換えることで
    ツールの実行をノンブロッキングにする。

    注意: この関数はモジュールレベルでクラスを書き換えるため、
    他のエージェントモジュールをインポートする **前** に呼び出すこと。
    """
    from handlers.human_approval_hook import HumanApprovalHook

    _original_init = HumanApprovalHook.__init__

    def _patched_init(self, approval_callback=None, approval_required_tools=None):
        # 自動承認コールバック（常に承認）
        _original_init(
            self,
            approval_callback=lambda tool_name, tool_params: (True, ""),
            approval_required_tools=approval_required_tools,
        )

    HumanApprovalHook.__init__ = _patched_init


# ============================================================
# モデル・状態ファクトリ
# ============================================================

def get_model():
    """評価器用のモデルを取得する。

    Returns:
        BedrockModel: 評価対象と同一のモデルインスタンス
    """
    from config.model_config import ModelConfig
    return ModelConfig.get_model()


def create_invocation_state(session_id: str) -> dict:
    """評価用の InvocationState を作成する。

    Args:
        session_id: テストケース固有のセッションID

    Returns:
        dict: InvocationState を model_dump() した辞書
    """
    from models.data_models import InvocationState

    state = InvocationState(
        user_name="評価テストユーザー",
        request_date=datetime.now().strftime("%Y-%m-%d"),
        session_id=session_id,
    )
    return state.model_dump()


# ============================================================
# エージェントファクトリ
# ============================================================

def create_orchestrator_agent(session_id: str) -> Agent:
    """評価用のオーケストレーターエージェントを作成する。

    既存の OrchestratorAgent クラスは input() ループを持つため直接使えない。
    同じ構成（モデル・プロンプト・ツール・フック）で Agent を直接生成する。

    Args:
        session_id: セッションID（テレメトリの trace_attributes に設定）

    Returns:
        Agent: 評価用オーケストレーターエージェント
    """
    from agents.general_expense_agent import general_expense_agent
    from agents.transportation_expense_agent import transportation_expense_agent
    from config.settings import settings
    from handlers.loop_control_hook import LoopControlHook
    from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
    from session.session_manager import SessionManagerFactory

    cfg = settings.orchestrator
    session_manager = SessionManagerFactory.create_session_manager(session_id)

    return Agent(
        model=get_model(),
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        tools=[transportation_expense_agent, general_expense_agent],
        agent_id="orchestrator_agent",
        name="申請受付窓口エージェント",
        description="社内申請の受付・種別判断・専門エージェントへの委譲を担当するオーケストレーター",
        callback_handler=None,
        conversation_manager=SlidingWindowConversationManager(
            window_size=cfg.window_size,
            should_truncate_results=True,
            per_turn=False,
        ),
        retry_strategy=ModelRetryStrategy(
            max_attempts=cfg.max_attempts,
            initial_delay=cfg.initial_delay,
            max_delay=cfg.max_delay,
        ),
        hooks=[LoopControlHook(max_iterations=cfg.max_iterations, agent_name="申請受付窓口エージェント")],
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
) -> list:
    """ActorSimulator を使ってエージェントと動的マルチターン会話を実行する。

    ActorSimulator が LLM ベースのユーザーシミュレータとして動的に応答を生成し、
    エージェントの応答に基づいて次のユーザー発話を決定する。

    Args:
        agent: strands Agent インスタンス
        case: strands_evals Case オブジェクト
        invocation_state_dict: InvocationState を model_dump() した dict
        max_turns: 最大ターン数

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
        # memory_exporter.clear() は呼ばない — 全ターンのスパンを蓄積する
        agent_response = agent(user_message, invocation_state=invocation_state_dict)
        response_str = str(agent_response)
        turns.append({"user_prompt": user_message, "agent_response": response_str})
        user_result = user_sim.act(response_str)
        user_message = str(user_result.structured_output.message)

    return turns
