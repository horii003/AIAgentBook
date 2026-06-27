"""申請受付窓口エージェント

社員の申請内容を受け付け、申請種別（交通費精算申請／経費精算申請）を判断し、
適切な専門エージェントへルーティングするオーケストレーター。
"""
import logging
from datetime import datetime

from strands import Agent, ModelRetryStrategy
from strands.agent.conversation_manager import SlidingWindowConversationManager

from agents.transportation_expense_agent import transportation_expense_agent
from agents.general_expense_agent import general_expense_agent
from config.model_config import ModelConfig
from config.settings import settings
from handlers.error_handler import ErrorHandler, LoopLimitError
from models.data_models import InvocationState
from handlers.loop_control_hook import LoopControlHook
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from session.session_manager import SessionManagerFactory

_logger = logging.getLogger(__name__)


class OrchestratorAgent:
    """申請受付窓口エージェント

    社員の申請内容を受け付け、申請種別（交通費精算申請／経費精算申請）を判断し、
    適切な専門エージェントへルーティングするオーケストレーター。
    """

    def __init__(self, applicant_name: str) -> None:
        """初期化する。

        Args:
            applicant_name: 申請者名
        """
        self._applicant_name = applicant_name
        self._session_id = SessionManagerFactory.generate_session_id()
        self._session_manager = SessionManagerFactory.create(self._session_id)
        self._agent = self._initialize_agent()
        _logger.info(
            "セッション開始: session_id=%s, applicant_name=%s",
            self._session_id, self._applicant_name,
        )

    def _initialize_agent(self) -> Agent:
        """Agent()インスタンスを生成する。

        Returns:
            Agent: 設定済みのAgentインスタンス
        """
        cfg = settings.orchestrator
        loop_control_hook = LoopControlHook(
            max_iterations=cfg.max_iterations,
            agent_name="申請受付窓口エージェント",
        )

        return Agent(
            model=ModelConfig.get_model(),
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            tools=[transportation_expense_agent, general_expense_agent],
            agent_id="orchestrator_agent",
            name="申請受付窓口エージェント",
            description="社員の申請内容を受け付け、申請種別を判断し、適切な専門エージェントへルーティングする受付窓口",
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
        """対話ループのメイン処理。"""
        print("============================================================")
        print("こちらは申請受付窓口エージェントです")
        print("社内の様々な申請作業をサポートします")
        print("")
        print("申請したい内容をお知らせください。キーワードでも構いません")
        print("")
        print("※終了するには 'exit' または 'quit' と入力ください")
        print("※最初からやり直すには 'reset' と入力ください")
        print("============================================================")

        while True:
            try:
                user_input = input("\n\n入力内容（終了時はquit）: ").strip()
                if not user_input:
                    continue

                if not self._handle_user_input(user_input):
                    break

            except KeyboardInterrupt:
                _logger.info(
                    "KeyboardInterruptによりセッションを終了します: session_id=%s",
                    self._session_id,
                )
                print("\n\n" + ErrorHandler.handle_keyboard_interrupt(KeyboardInterrupt()))
                break

        _logger.info("対話ループ終了: session_id=%s", self._session_id)

    def _handle_user_input(self, user_input: str) -> bool:
        """ユーザー入力を処理する。

        Args:
            user_input: ユーザーからの入力テキスト

        Returns:
            bool: 対話を継続する場合True、終了する場合False
        """
        # 終了コマンド判定
        if user_input.lower() in ("exit", "quit", "終了"):
            print("\nセッションを終了します。お疲れ様でした。")
            return False

        # リセットコマンド判定
        if user_input.lower() in ("reset", "リセット", "最初から"):
            self._reset_session()
            print("\nセッションをリセットしました。最初からやり直します。")
            print("申請内容を入力してください。")
            return True

        # 通常入力: エージェント実行
        response = self._execute_agent(user_input)
        print(f"\nシステム> {response}")
        return True

    def _execute_agent(self, user_input: str) -> str:
        """エージェントを実行し応答を取得する。

        Args:
            user_input: ユーザーからの入力テキスト

        Returns:
            str: エージェントの応答テキスト
        """
        invocation_state = InvocationState(
            applicant_name=self._applicant_name,
            application_date=datetime.now().strftime("%Y-%m-%d"),
            session_id=self._session_id,
        )

        try:
            response = self._agent(
                user_input,
                invocation_state=invocation_state.model_dump(),
            )
            return str(response)

        except KeyboardInterrupt as e:
            _logger.info(
                "KeyboardInterruptが発生しました: session_id=%s", self._session_id,
            )
            return ErrorHandler.handle_keyboard_interrupt(e)

        except LoopLimitError as e:
            _logger.warning(
                "LoopLimitErrorが発生しました: session_id=%s", self._session_id,
            )
            return ErrorHandler.handle_loop_limit_error(e)

        except RuntimeError as e:
            _logger.error(
                "RuntimeErrorが発生しました: session_id=%s", self._session_id,
                exc_info=True,
            )
            return ErrorHandler.handle_runtime_error(e)

        except Exception as e:
            _logger.error(
                "予期しないエラーが発生しました: session_id=%s", self._session_id,
                exc_info=True,
            )
            return ErrorHandler.handle_unexpected_error(e)

    def _reset_session(self) -> None:
        """セッションをリセットし、新しいセッションで再初期化する。"""
        old_session_id = self._session_id
        self._session_id = SessionManagerFactory.generate_session_id()
        self._session_manager = SessionManagerFactory.create(self._session_id)
        self._agent = self._initialize_agent()
        _logger.info(
            "セッションリセット: old=%s, new=%s", old_session_id, self._session_id,
        )
