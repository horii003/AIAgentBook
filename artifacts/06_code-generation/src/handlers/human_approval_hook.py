"""Human-in-the-Loop承認フック

申請書生成ツールの実行前に人間の承認を求め、
修正要望があれば修正を実行するフック。
"""
import logging
from typing import Any, Callable, Optional
from strands.hooks import HookProvider, HookRegistry, BeforeToolCallEvent
from handlers.console_approval_adapter import console_approval_callback

_logger = logging.getLogger(__name__)


class HumanApprovalHook(HookProvider):
    """指定ツール実行前に人間の承認を求めるフック。

    Hookは制御点として機能し、UI入力は呼び出し元から注入された approval_callback に委譲する。
    """

    def __init__(
        self,
        target_tools: list[str],
        approval_callback: Optional[Callable[[str, dict], tuple[bool, str]]] = None,
    ):
        """初期化

        Args:
            target_tools: 承認確認を行うツール名のリスト
            approval_callback: 承認を求めるコールバック関数。
                               引数: tool_name (str), tool_params (dict)
                               戻り値: tuple (approved: bool, feedback: str)
                               Noneの場合はデフォルトのCLI入力を使用。
        """
        self._target_tools = set(target_tools)
        self._approval_callback = approval_callback if approval_callback is not None else console_approval_callback

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録。

        BeforeToolCallEventは全ツール呼び出しで発火するため、
        ハンドラー内で対象ツールを必ずフィルタリングすること（R9.8.3参照）。
        """
        registry.add_callback(BeforeToolCallEvent, self._handle_before_tool_call)

    def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール実行前に承認を求める。"""
        tool_name = event.tool_use["name"] if event.tool_use else ""
        tool_params = event.tool_use["input"] or {} if event.tool_use else {}

        # 対象外ツールはスキップ
        if tool_name not in self._target_tools:
            return

        _logger.info("申請書生成の承認確認を開始します: tool=%s", tool_name)
        approved, message = self._approval_callback(tool_name, tool_params)

        if approved:
            _logger.info("申請書生成が承認されました: tool=%s", tool_name)
        elif message == "CANCEL" or not message:
            _logger.info("申請書生成がキャンセルされました: tool=%s", tool_name)
            event.cancel_tool = "申請がキャンセルされました。"
        else:
            _logger.info("申請書生成が修正要望でキャンセルされました: tool=%s", tool_name)
            event.cancel_tool = message
