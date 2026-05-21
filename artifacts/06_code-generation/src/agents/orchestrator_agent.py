"""オーケストレーターエージェント。

ユーザーからの依頼を受け付け、申請種別を判断して適切な専門エージェントに振り分ける。
申請受付窓口として機能する。
"""
import logging
from datetime import datetime

from strands import Agent, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager

from agents.general_expense_agent import general_expense_agent
from agents.transportation_expense_agent import transportation_expense_agent
from config.model_config import ModelConfig
from config.settings import settings
from handlers.error_handler import ErrorHandler, LoopLimitError
from handlers.loop_control_hook import LoopControlHook
from models.data_models import InvocationState
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from session.session_manager import SessionManagerFactory

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


class OrchestratorAgent:
    """オーケストレーターエージェントクラス。

    ユーザーとの対話を管理し、専門エージェントへの振り分けを行う。
    """

    def __init__(self):
        """初期化。"""
        self._session_id: str = ""
        self._session_manager = None
        self.agent: Agent = None
        self._user_name: str = ""

    def _initialize(self) -> None:
        """初期化処理。

        申請者名の収集・セッションID生成・Agent インスタンスの生成を行う。
        """
        # 申請者名を収集
        while not self._user_name:
            name = input("申請者名を入力してください: ").strip()
            if name:
                self._user_name = name
            else:
                print("申請者名を入力してください。")

        # セッションIDを生成
        self._session_id = SessionManagerFactory.generate_session_id()

        # セッションマネージャーを作成
        self._session_manager = SessionManagerFactory.create_session_manager(self._session_id)

        # LoopControlHook を作成
        cfg = settings.orchestrator
        loop_control_hook = LoopControlHook(
            max_iterations=cfg.max_iterations,
            agent_name="申請受付窓口エージェント",
        )

        # Agent インスタンスを生成
        self.agent = Agent(
            model=ModelConfig.get_model(),
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
            hooks=[loop_control_hook],
            session_manager=self._session_manager,
        )

        _logger.info("オーケストレーター初期化完了: session_id=%s", self._session_id)

    def run(self) -> None:
        """メインインタラクションループ。"""
        print(_WELCOME_MESSAGE)
        self._initialize()

        while True:
            try:
                user_input = input("\n\n入力内容（終了時はquit）: ").strip()

                # 終了条件
                if user_input.lower() in ("exit", "quit"):
                    print("セッションを終了します。")
                    break

                # リセット
                if user_input.lower() == "reset":
                    self._user_name = ""
                    self._initialize()
                    continue

                # 空文字
                if not user_input:
                    print("入力内容を入力してください。")
                    continue

                # 入力文字数チェック
                if len(user_input) > settings.orchestrator.max_input_length:
                    print(
                        f"入力内容は{settings.orchestrator.max_input_length}文字以内で入力してください。"
                    )
                    continue

                # invocation_state を構築
                invocation_state = InvocationState(
                    user_name=self._user_name,
                    request_date=datetime.now().strftime("%Y-%m-%d"),
                    session_id=self._session_id,
                )

                # エージェントを呼び出す
                response = self.agent(
                    user_input,
                    invocation_state=invocation_state.model_dump(),
                )
                print(str(response))

            except KeyboardInterrupt as e:
                _logger.info("キーボード中断: session_id=%s", self._session_id)
                print(ErrorHandler.handle_keyboard_interrupt(e))
                break
            except LoopLimitError as e:
                _logger.warning("ループ上限到達: session_id=%s", self._session_id)
                print(ErrorHandler.handle_loop_limit_error(e))
                continue
            except Exception as e:
                _logger.error(
                    "予期しないエラー: session_id=%s", self._session_id, exc_info=True
                )
                print(ErrorHandler.handle_unexpected_error(e))
                continue
