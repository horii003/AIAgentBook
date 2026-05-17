"""申請受付窓口エージェント（AG-001）

ユーザーからの申請内容を受け付け、適切な専門エージェントへ振り分ける。
"""

import logging
from datetime import datetime

from strands import Agent, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager

from agents.expense_agent import expense_agent
from agents.transport_agent import transport_agent
from config.model_config import ModelConfig
from config.settings import settings
from handlers.error_handler import ErrorHandler, LoopLimitError
from handlers.loop_control_hook import LoopControlHook
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from session.session_manager import SessionManagerFactory

_logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """申請受付窓口エージェント"""

    def __init__(self, applicant_name: str):
        """初期化

        Args:
            applicant_name: 申請者名
        """
        self._applicant_name = applicant_name
        self._session_id = SessionManagerFactory.generate_session_id()
        self._session_manager = SessionManagerFactory.create_session_manager(
            self._session_id
        )
        self._agent = self._build_agent()
        _logger.info(
            "オーケストレーター初期化: applicant=%s, session=%s",
            applicant_name,
            self._session_id,
        )

    def _build_agent(self) -> Agent:
        """Agent インスタンスを構築する"""
        cfg = settings.orchestrator
        loop_control_hook = LoopControlHook(
            max_iterations=cfg.max_iterations, agent_name="申請受付窓口エージェント"
        )

        return Agent(
            model=ModelConfig.get_model(),
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=[transport_agent, expense_agent],
            agent_id="orchestrator_agent",
            name="申請受付窓口エージェント",
            description="社員からの申請内容を受け付け、申請種別を判断し、適切な専門エージェントへ処理を委譲する",
            conversation_manager=SlidingWindowConversationManager(
                window_size=cfg.window_size,
                should_truncate_results=True,
                per_turn=False,
            ),
            callback_handler=None,
            retry_strategy=ModelRetryStrategy(
                max_attempts=cfg.max_attempts,
                initial_delay=cfg.initial_delay,
                max_delay=cfg.max_delay,
            ),
            session_manager=self._session_manager,
            hooks=[loop_control_hook],
        )

    def run(self) -> None:
        """メインインタラクションループを実行する"""
        print("経費精算・交通費精算申請システムへようこそ。")
        print(f"申請者: {self._applicant_name}")
        print("申請内容を入力してください（終了: 'quit' または Ctrl+C）\n")

        while True:
            try:
                user_input = input("あなた> ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "終了"):
                    print("ご利用ありがとうございました。")
                    break

                invocation_state = {
                    "applicant_name": self._applicant_name,
                    "application_date": datetime.now().strftime("%Y-%m-%d"),
                    "session_id": self._session_id,
                }

                response = self._agent(
                    user_input, invocation_state=invocation_state
                )
                print(f"\nエージェント> {response}\n")

            except LoopLimitError as e:
                _logger.warning("ループ制限到達: session=%s", self._session_id)
                print(f"\n{ErrorHandler.handle_loop_limit_error(e)}\n")
            except KeyboardInterrupt:
                print(f"\n{ErrorHandler.handle_keyboard_interrupt(KeyboardInterrupt())}")
                break
            except Exception as e:
                _logger.error("予期しないエラー: %s", e, exc_info=True)
                print(f"\n{ErrorHandler.handle_unexpected_error(e)}\n")
