"""オーケストレーターエージェント

申請受付窓口エージェント（AG-001）。
ユーザーからの申請内容を受け付け、適切な専門エージェントへ振り分ける。
"""
import logging
from datetime import datetime
from strands import Agent, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from session.session_manager import SessionManagerFactory
from handlers.error_handler import ErrorHandler, LoopLimitError
from handlers.loop_control_hook import LoopControlHook
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from config.model_config import ModelConfig
from config.settings import settings
from models.data_models import InvocationState

_logger = logging.getLogger(__name__)

_WELCOME_MESSAGE = """============================================================
こちらは申請受付窓口エージェントです
社内の様々な申請作業をサポートします

最初に申請者名を入力してください。その後、申請したい内容をお知らせください。キーワードでも構いません

※終了するには 'exit' または 'quit' と入力ください
※最初からやり直すには 'reset' と入力ください
============================================================"""

_EXIT_COMMANDS = {"exit", "quit", "終了"}
_RESET_COMMANDS = {"reset", "リセット", "最初から"}


class OrchestratorAgent:
    """申請受付窓口エージェント（AG-001）

    ユーザーとの対話を管理し、専門エージェントへの振り分けを行う。
    """

    def __init__(self, applicant_name: str, session_id: str):
        """初期化。

        Args:
            applicant_name: 申請者名
            session_id: セッションID
        """
        self._applicant_name = applicant_name
        self._session_id = session_id
        self._session_manager = None
        self.agent = None
        self._initialize()

    def _initialize(self) -> None:
        """エージェントを初期化する。"""
        # 専門エージェントのインポートは循環インポートを避けるため遅延インポート
        from agents.expense_agent import expense_agent
        from agents.transport_agent import transport_agent

        self._session_manager = SessionManagerFactory.create_session_manager(self._session_id)
        cfg = settings.orchestrator
        loop_control_hook = LoopControlHook(
            max_iterations=cfg.max_iterations,
            agent_name="申請受付窓口エージェント",
        )
        self.agent = Agent(
            model=ModelConfig.get_model(),
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=[expense_agent, transport_agent],
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
            hooks=[loop_control_hook],
            session_manager=self._session_manager,
        )

    def run(self) -> None:
        """メインインタラクションループを実行する。"""
        # 遅延インポート（_initialize と同じ理由）
        from strands.types.exceptions import ContextWindowOverflowException, MaxTokensReachedException

        print(_WELCOME_MESSAGE)
        cfg = settings.orchestrator

        for _ in range(cfg.max_turn_count):
            try:
                user_input = input("\n\n入力内容（終了時はquit）: ").strip()
            except (EOFError, KeyboardInterrupt):
                _logger.info("キーボード割り込み: session_id=%s", self._session_id)
                print(ErrorHandler.handle_keyboard_interrupt())
                break

            if not user_input:
                print("入力してください。")
                continue

            if user_input.lower() in _EXIT_COMMANDS:
                print("ご利用ありがとうございました。")
                break

            if user_input.lower() in _RESET_COMMANDS:
                self.agent.messages.clear()
                self._applicant_name = input("申請者名を入力してください: ").strip()
                print("会話をリセットしました。")
                continue

            if len(user_input) > cfg.max_input_length:
                print(f"入力が長すぎます（{cfg.max_input_length}文字以内）。")
                continue

            invocation_state = InvocationState(
                applicant_name=self._applicant_name,
                application_date=datetime.now().strftime("%Y-%m-%d"),
                session_id=self._session_id,
            ).model_dump()

            try:
                response = self.agent(user_input, invocation_state=invocation_state)
                print(response)
            except KeyboardInterrupt:
                _logger.info("キーボード割り込み: session_id=%s", self._session_id)
                print(ErrorHandler.handle_keyboard_interrupt())
                break
            except LoopLimitError as e:
                _logger.warning("ループ制限到達: session_id=%s", self._session_id)
                print(ErrorHandler.handle_loop_limit_error(e))
                continue
            except ContextWindowOverflowException as e:
                _logger.warning("コンテキストウィンドウ超過: session_id=%s", self._session_id)
                print(ErrorHandler.handle_context_window_error(e))
                continue
            except MaxTokensReachedException as e:
                _logger.warning("最大トークン数到達: session_id=%s", self._session_id)
                print(ErrorHandler.handle_max_tokens_error(e))
                continue
            except RuntimeError as e:
                _logger.error("実行時エラー: session_id=%s", self._session_id, exc_info=True)
                print(ErrorHandler.handle_runtime_error(e))
                continue
            except Exception as e:
                _logger.error("予期しないエラー: session_id=%s", self._session_id, exc_info=True)
                print(ErrorHandler.handle_unexpected_error(e))
                continue
