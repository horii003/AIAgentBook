"""Human-in-the-Loop承認フック

申請書生成ツールの実行前に人間の承認を求めるフック。
承認コールバックを通じてUIとのやりとりを行う。
"""
import logging
from typing import Any, Callable, Optional
from strands.hooks import HookProvider, HookRegistry, BeforeToolCallEvent

_logger = logging.getLogger(__name__)


class HumanApprovalHook(HookProvider):
    """指定ツール実行前に人間の承認を求めるフック。

    Hookは制御点として機能し、UI入力は呼び出し元から注入された approval_callback に委譲する。
    """

    APPROVAL_REQUIRED_TOOLS: frozenset = frozenset({
        "generate_expense_report",
        "generate_transport_report",
    })

    def __init__(
        self,
        approval_callback: Callable[[str, dict], tuple],
        approval_required_tools: Optional[list] = None,
    ):
        """初期化。

        Args:
            approval_callback: 承認を求めるコールバック関数。
                               引数: tool_name (str), tool_params (dict)
                               戻り値: tuple (approved: bool, feedback: str)
                                 (True,  "")         : 承認
                                 (False, "CANCEL")   : キャンセル
                                 (False, "修正内容") : 修正要望
            approval_required_tools: 承認対象とするツール名のリスト。
                               None の場合はデフォルト（APPROVAL_REQUIRED_TOOLS）を使用。
        """
        self.approval_callback = approval_callback
        self.approval_required_tools: frozenset = (
            frozenset(approval_required_tools)
            if approval_required_tools is not None
            else self.APPROVAL_REQUIRED_TOOLS
        )

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録。"""
        registry.add_callback(BeforeToolCallEvent, self._on_before_tool_call)

    def _on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール実行前に承認を求める。

        Args:
            event: BeforeToolCallEvent
        """
        tool_name = event.tool_use.get("name", "") if event.tool_use else ""
        tool_params = event.tool_use.get("input", {}) if event.tool_use else {}

        # 対象外ツールはスキップ
        if tool_name not in self.approval_required_tools:
            return

        _logger.info("承認確認: ツール [%s]", tool_name)
        approved, feedback = self.approval_callback(tool_name, tool_params)

        if approved:
            _logger.info("承認済み: ツール [%s]", tool_name)
            return

        # 非承認: キャンセルメッセージを設定
        cancel_message = self._build_cancel_message(tool_name, feedback)
        event.cancel_tool = cancel_message

    def _build_cancel_message(self, tool_name: str, feedback: str) -> str:
        """キャンセルメッセージを生成する。

        Args:
            tool_name: ツール名
            feedback: ユーザーからのフィードバック（"CANCEL"=拒否、それ以外=修正要望、空=拒否）

        Returns:
            str: LLMへ返却するキャンセルメッセージ
        """
        if not feedback or feedback == "CANCEL":
            return (
                f"ユーザーが申請書の生成をキャンセルしました。"
                "申請を中止し、ユーザーに中止した旨を伝えてください。"
            )
        return (
            f"ユーザーから以下の修正要望があります。内容を修正して再度申請書を生成してください。\n"
            f"修正要望: {feedback}"
        )
