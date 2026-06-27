"""ReActループ制御フック

エージェントのReActループの最大回数を制御し、
ループの状態を表示するフック。
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
    """ReActループの最大回数を制御するフック。

    このフックは以下の機能を提供します：
    1. BeforeInvocationEventでループカウントを初期化
    2. AfterModelCallEventでループカウントをインクリメント
    3. 最大回数に達した場合はLoopLimitErrorを発生させる
    4. エージェントのフロー（状態）を表示
    """

    def __init__(self, max_iterations: int = 10, agent_name: str = "unknown") -> None:
        """初期化する。

        Args:
            max_iterations: 最大ループ回数（デフォルト: 10）
            agent_name: エージェント名（ログ表示用）
        """
        self._max_iterations = max_iterations
        self._agent_name = agent_name
        self._loop_count = 0

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録。"""
        registry.add_callback(BeforeInvocationEvent, self._handle_before_invocation)
        registry.add_callback(BeforeModelCallEvent, self._handle_before_model_call)
        registry.add_callback(AfterModelCallEvent, self._handle_after_model_call)
        registry.add_callback(BeforeToolCallEvent, self._handle_before_tool_call)
        registry.add_callback(AfterToolCallEvent, self._handle_after_tool_call)
        registry.add_callback(AfterInvocationEvent, self._handle_after_invocation)

    def _handle_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """エージェント呼び出し開始前の処理。

        Args:
            event: BeforeInvocationEvent
        """
        self._loop_count = 0
        _logger.info("エージェント呼び出し開始: %s", self._agent_name)

    def _handle_before_model_call(self, event: BeforeModelCallEvent) -> None:
        """モデル呼び出し前の処理。

        Args:
            event: BeforeModelCallEvent
        """
        _logger.info("ループ回数: %d/%d", self._loop_count + 1, self._max_iterations)

    def _handle_after_model_call(self, event: AfterModelCallEvent) -> None:
        """モデル呼び出し後の処理。

        Args:
            event: AfterModelCallEvent
        """
        # 例外発生時はスキップ
        if event.exception:
            return

        self._loop_count += 1
        _logger.info("モデル呼び出し完了: ループ回数=%d", self._loop_count)

        if self._loop_count >= self._max_iterations:
            _logger.warning(
                "ループ制御: エージェント '%s' の最大回数(%d回)に到達しました。現在のカウント: %d",
                self._agent_name,
                self._max_iterations,
                self._loop_count,
            )
            raise LoopLimitError(
                current_iteration=self._loop_count,
                max_iterations=self._max_iterations,
                agent_name=self._agent_name,
            )

    def _get_tool_name(self, event) -> str:
        """ツール名を安全に取得するヘルパー（R9.8.6参照）。"""
        return event.tool_use["name"] if event.tool_use else "unknown"

    def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール呼び出し前の処理。

        Args:
            event: BeforeToolCallEvent
        """
        tool_name = self._get_tool_name(event)
        _logger.info("ツール呼び出し開始: %s", tool_name)

    def _handle_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """ツール呼び出し後の処理。

        Args:
            event: AfterToolCallEvent
        """
        tool_name = self._get_tool_name(event)
        _logger.info("ツール呼び出し完了: %s", tool_name)

    def _handle_after_invocation(self, event: AfterInvocationEvent) -> None:
        """エージェント呼び出し終了時の処理。

        Args:
            event: AfterInvocationEvent
        """
        _logger.info("エージェント呼び出し完了: 合計ループ回数=%d", self._loop_count)
