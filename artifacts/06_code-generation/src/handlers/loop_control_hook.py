"""ReActループ制御フック。

エージェントのReActループの最大回数を制御し、
ループの状態をログ出力するフック。全エージェントで共通利用する。
"""
import logging
from typing import Any

from strands.hooks import (
    AfterInvocationEvent,
    AfterModelCallEvent,
    AfterToolCallEvent,
    BeforeInvocationEvent,
    BeforeModelCallEvent,
    BeforeToolCallEvent,
    HookProvider,
    HookRegistry,
)

from handlers.error_handler import LoopLimitError

_logger = logging.getLogger(__name__)


class LoopControlHook(HookProvider):
    """ReActループの最大回数を制御するフック。

    以下の機能を提供する:
    1. BeforeInvocationEventでループカウントを初期化
    2. AfterModelCallEventでループカウントをインクリメント
    3. 最大回数に達した場合はLoopLimitErrorを発生させる
    4. エージェントのフロー（状態）をログ出力する
    """

    def __init__(self, max_iterations: int = 10, agent_name: str = "Agent"):
        """初期化。

        Args:
            max_iterations: 最大ループ回数（デフォルト: 10）
            agent_name: エージェント名（ログ表示用）
        """
        self._max_iterations = max_iterations
        self.agent_name = agent_name
        self._current_iteration = 0

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックを登録する。

        Args:
            registry: フックレジストリ
        """
        registry.add_callback(BeforeInvocationEvent, self.on_before_invocation)
        registry.add_callback(BeforeModelCallEvent, self.on_before_model_call)
        registry.add_callback(AfterModelCallEvent, self.on_after_model_call)
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)
        registry.add_callback(AfterToolCallEvent, self.on_after_tool_call)
        registry.add_callback(AfterInvocationEvent, self.on_after_invocation)

    def on_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """エージェント呼び出し開始前の処理。ループカウンタをリセットする。

        Args:
            event: BeforeInvocationEvent
        """
        self._current_iteration = 0
        _logger.info("エージェント呼び出し開始: %s", self.agent_name)

    def on_before_model_call(self, event: BeforeModelCallEvent) -> None:
        """モデル呼び出し前の処理。現在のループ回数をログ出力する。

        Args:
            event: BeforeModelCallEvent
        """
        _logger.info(
            "ループ回数: %d / %d",
            self._current_iteration + 1,
            self._max_iterations,
        )

    def on_after_model_call(self, event: AfterModelCallEvent) -> None:
        """モデル呼び出し後の処理。ループカウンタをインクリメントし上限を監視する。

        Args:
            event: AfterModelCallEvent
        """
        # 例外発生時はカウントアップをスキップする
        if getattr(event, "exception", None) is not None:
            return

        self._current_iteration += 1

        if self._current_iteration >= self._max_iterations:
            _logger.warning(
                "ループ上限到達: %d / %d",
                self._current_iteration,
                self._max_iterations,
            )
            raise LoopLimitError(
                current_iteration=self._current_iteration,
                max_iterations=self._max_iterations,
                agent_name=self.agent_name,
            )

    def _get_tool_name(self, event) -> str:
        """ツール名を安全に取得するヘルパー（R9.8.6参照）。

        Args:
            event: BeforeToolCallEvent または AfterToolCallEvent

        Returns:
            str: ツール名。tool_useがNoneの場合は "unknown"
        """
        return event.tool_use["name"] if event.tool_use else "unknown"

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール呼び出し前の処理。ツール名をログ出力する。

        Args:
            event: BeforeToolCallEvent
        """
        tool_name = self._get_tool_name(event)
        _logger.info("ツール呼び出し開始: %s", tool_name)

    def on_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """ツール呼び出し後の処理。ツール名をログ出力する。

        Args:
            event: AfterToolCallEvent
        """
        tool_name = self._get_tool_name(event)
        _logger.info("ツール呼び出し完了: %s", tool_name)

    def on_after_invocation(self, event: AfterInvocationEvent) -> None:
        """エージェント呼び出し終了時の処理。合計ループ回数をログ出力する。

        Args:
            event: AfterInvocationEvent
        """
        _logger.info("合計ループ回数: %d", self._current_iteration)
