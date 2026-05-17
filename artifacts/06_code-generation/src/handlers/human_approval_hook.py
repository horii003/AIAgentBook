"""Human-in-the-Loop承認フック

申請書生成ツール実行前にユーザーの承認を得る機構を提供する。
"""

import logging
from typing import Any, Callable, Tuple

from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

_logger = logging.getLogger(__name__)


def console_approval_callback(tool_name: str, tool_params: dict) -> Tuple[bool, str]:
    """CLI用のデフォルト承認コールバック"""
    print("\n申請書を生成してよろしいですか？")
    print("1. OK（生成する）")
    print("2. 修正（情報を修正する）")
    print("3. キャンセル（申請を中止する）")
    choice = input("> ").strip()
    if choice in ("1", "ok", "OK"):
        return (True, "")
    elif choice in ("2", "修正"):
        correction = input("修正内容を入力してください: ").strip()
        return (False, correction if correction else "修正を選択しました。情報を修正してください。")
    else:
        return (False, "CANCEL")


class HumanApprovalHook(HookProvider):
    """申請書生成ツール実行前にユーザーの承認を得るフック"""

    def __init__(
        self,
        target_tools: list[str],
        approval_callback: Callable[[str, dict], Tuple[bool, str]] | None = None,
    ):
        """初期化

        Args:
            target_tools: 承認対象のツール名リスト
            approval_callback: 承認コールバック関数（未指定時はCLI承認）
        """
        self._target_tools = target_tools
        self._approval_callback = approval_callback or console_approval_callback

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックイベントをレジストリに登録する"""
        registry.add_callback(BeforeToolCallEvent, self._handle_before_tool_call)

    def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール実行前に承認ゲートを実行する"""
        tool_name = event.tool_use["name"]

        # 対象ツール以外はスキップ
        if tool_name not in self._target_tools:
            return

        _logger.info("承認ゲート発火: tool_name=%s", tool_name)

        tool_params = event.tool_use["input"] or {}
        approved, message = self._approval_callback(tool_name, tool_params)

        if approved:
            _logger.info("承認: OK が選択されました")
            return

        if message == "CANCEL":
            _logger.info("承認: キャンセル が選択されました")
            event.cancel_tool = "キャンセルを選択しました。申請処理を終了します。"
        else:
            _logger.info("承認: 修正 が選択されました")
            event.cancel_tool = message
