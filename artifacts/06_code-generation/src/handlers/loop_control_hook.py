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
    """ReActループの最大回数を制御するフック

    このフックは以下の機能を提供します：
    1. BeforeInvocationEventでループカウントを初期化
    2. AfterModelCallEventでループカウントをインクリメント
    3. 最大回数に達した場合はLoopLimitErrorを発生させる
    4. エージェントのフロー（状態）を表示
    """

    def __init__(self, max_iterations: int = 10, agent_name: str = "Agent"):
        """初期化

        Args:
            max_iterations: 最大ループ回数（デフォルト: 10）
            agent_name: エージェント名（ログ表示用）
        """
        self._max_iterations = max_iterations
        self._agent_name = agent_name
        self._iteration_count = 0

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録"""
        registry.add_callback(BeforeInvocationEvent, self._handle_before_invocation)
        registry.add_callback(BeforeModelCallEvent, self._handle_before_model_call)
        registry.add_callback(AfterModelCallEvent, self._handle_after_model_call)
        registry.add_callback(BeforeToolCallEvent, self._handle_before_tool_call)
        registry.add_callback(AfterToolCallEvent, self._handle_after_tool_call)
        registry.add_callback(AfterInvocationEvent, self._handle_after_invocation)

    def _get_tool_name(self, event) -> str:
        """ツール名を安全に取得するヘルパー（R9.8.6参照）"""
        return event.tool_use["name"] if event.tool_use else "unknown"

    def _handle_before_invocation(self, event: BeforeInvocationEvent) -> None:
        """エージェント呼び出し開始時の処理"""
        self._iteration_count = 0
        _logger.info("エージェント呼び出し開始: agent=%s", self._agent_name)

    def _handle_before_model_call(self, event: BeforeModelCallEvent) -> None:
        """モデル呼び出し前の処理"""
        _logger.info(
            "LLM呼び出し開始: iteration=%d/%d",
            self._iteration_count + 1,
            self._max_iterations,
        )

    def _handle_after_model_call(self, event: AfterModelCallEvent) -> None:
        """モデル呼び出し後の処理"""
        # 例外発生時はスキップ
        if event.exception is not None:
            return
        self._iteration_count += 1
        _logger.info(
            "LLM呼び出し完了: iteration=%d/%d",
            self._iteration_count,
            self._max_iterations,
        )
        if self._iteration_count >= self._max_iterations:
            _logger.warning(
                "ループ上限に達しました: iteration=%d, max=%d",
                self._iteration_count,
                self._max_iterations,
            )
            raise LoopLimitError(
                current_iteration=self._iteration_count,
                max_iterations=self._max_iterations,
                agent_name=self._agent_name,
            )

    def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール呼び出し前の処理"""
        tool_name = self._get_tool_name(event)
        _logger.info("ツール呼び出し開始: tool=%s", tool_name)

    def _handle_after_tool_call(self, event: AfterToolCallEvent) -> None:
        """ツール呼び出し後の処理"""
        tool_name = self._get_tool_name(event)
        _logger.info("ツール呼び出し完了: tool=%s", tool_name)

    def _handle_after_invocation(self, event: AfterInvocationEvent) -> None:
        """エージェント呼び出し終了時の処理"""
        _logger.info("エージェント呼び出し完了: 合計ループ回数=%d", self._iteration_count)
