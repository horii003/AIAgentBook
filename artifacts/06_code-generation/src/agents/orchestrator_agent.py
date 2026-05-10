"""オーケストレーターエージェント

ユーザーからの依頼を受け付け、適切な専門エージェントに振り分ける。
申請受付窓口として機能する。
"""
import logging
from datetime import datetime
from strands import Agent, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager
from strands.types.exceptions import ContextWindowOverflowException, MaxTokensReachedException
from agents.transport_agent import transport_agent
from agents.expense_agent import expense_agent
from session.session_manager import SessionManagerFactory
from handlers.error_handler import ErrorHandler
from handlers.loop_control_hook import LoopControlHook, LoopLimitError
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from config.model_config import ModelConfig
from config.settings import settings

_logger = logging.getLogger(__name__)

# ウェルカムメッセージ
_WELCOME_MESSAGE = """
============================================================
こちらは申請受付窓口エージェントです
社内の様々な申請作業をサポートします

最初に申請者名を入力してください。その後、申請したい内容をお知らせください。キーワードでも構いません

※終了するには 'exit' または 'quit' と入力ください
※最初からやり直すには 'reset' と入力ください
============================================================
"""

# 終了コマンド
_EXIT_COMMANDS = {"exit", "quit", "終了"}
# リセットコマンド
_RESET_COMMANDS = {"reset", "リセット", "最初から"}


class OrchestratorAgent:
    """オーケストレーターエージェントクラス

    ユーザーとの対話を管理し、専門エージェントへの振り分けを行う。
    """

    def __init__(self, session_id: str):
        """初期化

        Args:
            session_id: セッションID（main.pyで生成して渡す）
        """
        self._session_id = session_id
        self._user_name = ""
        self._session_manager = None
        self.agent = None

    def _collect_user_name(self) -> None:
        """CLI標準入力で申請者名を収集する（空文字の場合は再入力を促す）"""
        while True:
            name = input("申請者名を入力してください: ").strip()
            if name:
                self._user_name = name
                _logger.info("申請者名を収集しました: %s", name)
                print(f"\n{name} さん、ようこそ。")
                print("申請したい内容をご入力ください。（例：「交通費の申請をしたい」「備品を購入したので経費申請したい」）")
                break
            print("申請者名を入力してください。")

    def _build_agent(self) -> None:
        """Strandsエージェントインスタンスを生成する"""
        self._session_manager = SessionManagerFactory.create_session_manager(self._session_id)
        loop_control_hook = LoopControlHook(
            max_iterations=settings.orchestrator.max_iterations,
            agent_name="申請受付窓口エージェント",
        )
        self.agent = Agent(
            model=ModelConfig.get_model(),
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=[transport_agent, expense_agent],
            agent_id="orchestrator_agent",
            name="申請受付窓口エージェント",
            description="申請種別を判断し、交通費精算申請エージェントまたは経費精算申請エージェントへ処理を委譲する",
            conversation_manager=SlidingWindowConversationManager(
                window_size=settings.orchestrator.window_size,
                should_truncate_results=True,
                per_turn=False,
            ),
            callback_handler=None,
            retry_strategy=ModelRetryStrategy(
                max_attempts=settings.orchestrator.max_attempts,
                initial_delay=settings.orchestrator.initial_delay,
                max_delay=settings.orchestrator.max_delay,
            ),
            hooks=[loop_control_hook],
            session_manager=self._session_manager,
        )

    def run(self) -> None:
        """メインインタラクションループ"""
        print(_WELCOME_MESSAGE)
        _logger.info("申請受付窓口エージェントを起動しました: session_id=%s", self._session_id)

        while True:
            # 申請者名収集
            self._collect_user_name()
            self._build_agent()

            # 対話ループ
            while True:
                try:
                    user_input = input("\n\n入力内容（終了時はquit）: ").strip()
                except KeyboardInterrupt:
                    print(ErrorHandler.handle_keyboard_interrupt())
                    _logger.info("ユーザーによる中断: session_id=%s", self._session_id)
                    return

                if not user_input:
                    continue

                # 終了コマンド
                if user_input.lower() in _EXIT_COMMANDS:
                    print("ご利用ありがとうございました。")
                    return

                # リセットコマンド
                if user_input.lower() in _RESET_COMMANDS:
                    print("最初からやり直します。")
                    break

                # invocation_stateを辞書リテラルで渡す
                invocation_state = {
                    "applicant_name": self._user_name,
                    "application_date": datetime.now().strftime("%Y-%m-%d"),
                    "session_id": self._session_id,
                }

                try:
                    response = self.agent(user_input, invocation_state=invocation_state)
                    print(str(response))
                except KeyboardInterrupt:
                    print(ErrorHandler.handle_keyboard_interrupt())
                    _logger.info("ユーザーによる中断: session_id=%s", self._session_id)
                    return
                except LoopLimitError as e:
                    _logger.warning("ループ上限に達しました: session_id=%s", self._session_id)
                    print(ErrorHandler.handle_loop_limit_error(e))
                except ContextWindowOverflowException as e:
                    _logger.warning("コンテキストウィンドウ超過: session_id=%s", self._session_id)
                    print(ErrorHandler.handle_context_window_error(e))
                except MaxTokensReachedException as e:
                    _logger.warning("最大トークン数到達: session_id=%s", self._session_id)
                    print(ErrorHandler.handle_max_tokens_error(e))
                except RuntimeError as e:
                    _logger.error("実行時エラーが発生しました: session_id=%s", self._session_id, exc_info=True)
                    print(ErrorHandler.handle_runtime_error(e))
                except Exception as e:
                    _logger.error("予期しないエラーが発生しました: session_id=%s", self._session_id, exc_info=True)
                    print(ErrorHandler.handle_unexpected_error(e))
