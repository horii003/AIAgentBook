"""ReActループ制御フック

全エージェントのReActループを監視し、最大ループ回数到達時にLoopLimitErrorを発生させる。
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
    """ReActループ回数を監視して無限ループを防止するフック"""

    def __init__(self, max_iterations: int = 10, agent_name: str = ""):
        """初期化

        Args:
            max_iterations: ReActループの最大回数
            agent_name: エージェント名（ログ・エラーメッセージ用）
        """
        self._max_iterations = max_iterations
        self._agent_name = agent_name
        self._iteration_count = 0

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックイベントをレジストリに登録する"""
        registry.add_callback(BeforeInvocationEvent, self._handle_before_invocation)
        registry.add_callback(BeforeModelCallEvent, self._handle_before_model_call)
        registry.add_callback(AfterModelCallEvent, self._handle_after_model_call)
        registry.add_callback(BeforeToolCallEvent, self._handle_before_tool_call)
        registry.add_callback(AfterToolCallEvent, self._handle_after_tool_call)
        registry.add_callback(AfterInvocationEvent, self._handle_after_invocation)

    def _get_tool_name(self, event: Any) -> str:
        """ツール名を安全に取得するヘルパー"""
        return event.tool_use["name"] if event.tool_use else "unknown"

    def _handle_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """エージェント呼び出し開始前にカウンタをリセットする"""
        self._iteration_count = 0

    def _handle_before_model_call(self, event: BeforeModelCallEvent) -> None:
        """LLM呼び出し前にループ回数をログ出力する"""
        _logger.info(
            "モデル呼び出し開始: agent_name=%s, iteration=%d/%d",
            self._agent_name,
            self._iteration_count + 1,
            self._max_iterations,
        )

    def _handle_after_model_call(self, event: AfterModelCallEvent) -> None:
        """LLM呼び出し後にカウンタをインクリメントし上限を監視する"""
        if event.exception:
            return
        self._iteration_count += 1
        if self._iteration_count >= self._max_iterations:
            _logger.warning(
                "ループ制限到達: agent_name=%s, iteration=%d/%d",
                self._agent_name,
                self._iteration_count,
                self._max_iterations,
            )
            raise LoopLimitError(
                current_iteration=self._iteration_count,
                max_iterations=self._max_iterations,
                agent_name=self._agent_name,
            )

    def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール実行前にツール名をログ出力する"""
        tool_name = self._get_tool_name(event)
        _logger.info(
            "ツール呼び出し開始: tool_name=%s, agent_name=%s",
            tool_name,
            self._agent_name,
        )

    def _handle_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """ツール実行後にツール名をログ出力する"""
        tool_name = self._get_tool_name(event)
        _logger.info(
            "ツール呼び出し完了: tool_name=%s, agent_name=%s",
            tool_name,
            self._agent_name,
        )

    def _handle_after_invocation(self, event: AfterInvocationEvent) -> None:
        """エージェント呼び出し完了後に合計ループ回数をログ出力する"""
        _logger.info(
            "エージェント呼び出し完了: agent_name=%s, 合計ループ回数=%d",
            self._agent_name,
            self._iteration_count,
        )
