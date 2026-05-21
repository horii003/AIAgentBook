"""ReActループ制御フック

エージェントのReActループの最大回数を制御し、ループの状態を表示するフック。
"""
import logging
from typing import Any
from strands.hooks import (
    HookProvider,
    HookRegistry,
    BeforeInvocationEvent,
    AfterModelCallEvent,
    BeforeModelCallEvent,
    AfterInvocationEvent,
    BeforeToolCallEvent,
    AfterToolCallEvent,
)
from handlers.error_handler import LoopLimitError

_logger = logging.getLogger(__name__)


class LoopControlHook(HookProvider):
    """ReActループの最大回数を制御するフック

    BeforeInvocationEventでループカウントを初期化し、
    AfterModelCallEventでインクリメント。最大回数到達時に LoopLimitError を raise する。
    """

    def __init__(self, max_iterations: int = 10, agent_name: str = "Agent"):
        """初期化。

        Args:
            max_iterations: 最大ループ回数（デフォルト: 10）
            agent_name: エージェント名（ログ表示用）
        """
        self.max_iterations = max_iterations
        self.agent_name = agent_name
        self.current_iteration = 0

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録。"""
        registry.add_callback(BeforeInvocationEvent, self.on_before_invocation)
        registry.add_callback(BeforeModelCallEvent, self.on_before_model_call)
        registry.add_callback(AfterModelCallEvent, self.on_after_model_call)
        registry.add_callback(BeforeToolCallEvent, self.on_before_tool_call)
        registry.add_callback(AfterToolCallEvent, self.on_after_tool_call)
        registry.add_callback(AfterInvocationEvent, self.on_after_invocation)

    def on_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """エージェント呼び出し開始時の処理。ループカウントを初期化する。

        Args:
            event: BeforeInvocationEvent
        """
        self.current_iteration = 0
        _logger.info("%s: 呼び出し開始", self.agent_name)

    def on_before_model_call(self, event: BeforeModelCallEvent) -> None:
        """モデル呼び出し前の処理。現在のループ回数をログ出力する。

        Args:
            event: BeforeModelCallEvent
        """
        _logger.info("%s: モデル呼び出し（ループ %d 回目）", self.agent_name, self.current_iteration + 1)

    def on_after_model_call(self, event: AfterModelCallEvent) -> None:
        """モデル呼び出し後の処理。カウントをインクリメントし、上限チェックを行う。

        Args:
            event: AfterModelCallEvent

        Raises:
            LoopLimitError: ループ回数が上限に達した場合
        """
        # 例外発生時はスキップ
        if event.exception is not None:
            return
        self.current_iteration += 1
        if self.current_iteration >= self.max_iterations:
            _logger.warning(
                "%s: ループ上限到達（%d/%d）",
                self.agent_name, self.current_iteration, self.max_iterations,
            )
            raise LoopLimitError(self.current_iteration, self.max_iterations, self.agent_name)

    def _get_tool_name(self, event) -> str:
        """ツール名を安全に取得するヘルパー。

        Args:
            event: BeforeToolCallEvent または AfterToolCallEvent

        Returns:
            str: ツール名。tool_use が None の場合は "unknown"
        """
        return event.tool_use["name"] if event.tool_use else "unknown"

    def on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール呼び出し前の処理。ツール名をログ出力する。

        Args:
            event: BeforeToolCallEvent
        """
        tool_name = self._get_tool_name(event)
        _logger.info("%s: ツール呼び出し開始 [%s]", self.agent_name, tool_name)

    def on_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """ツール呼び出し後の処理。ツール名をログ出力する。

        Args:
            event: AfterToolCallEvent
        """
        tool_name = self._get_tool_name(event)
        _logger.info("%s: ツール呼び出し完了 [%s]", self.agent_name, tool_name)

    def on_after_invocation(self, event: AfterInvocationEvent) -> None:
        """エージェント呼び出し終了時の処理。合計ループ回数をログ出力する。

        Args:
            event: AfterInvocationEvent
        """
        _logger.info("%s: 呼び出し完了（合計ループ回数: %d）", self.agent_name, self.current_iteration)
