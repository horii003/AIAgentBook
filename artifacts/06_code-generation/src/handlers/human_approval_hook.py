"""Human-in-the-Loop承認フック

申請書生成ツールの実行前に人間の承認を求め、
修正要望があれば修正を実行するフック。
"""
import logging
from typing import Any, Callable, Optional

from strands.hooks import HookProvider, HookRegistry, BeforeToolCallEvent

_logger = logging.getLogger(__name__)


class HumanApprovalHook(HookProvider):
    """指定ツール実行前に人間の承認を求めるフック。

    Hookは制御点として機能し、UI入力は呼び出し元から注入された approval_callback に委譲する。
    """

    def __init__(
        self,
        target_tools: list[str],
        approval_callback: Optional[Callable[[str, dict], tuple]] = None,
    ) -> None:
        """初期化する。

        Args:
            target_tools: 承認対象のツール名リスト
            approval_callback: 承認コールバック関数（省略時はデフォルトの対話処理を使用）
                シグネチャ: (tool_name: str, tool_params: dict) -> tuple[bool, str]
                戻り値: (True, "") → OK、(False, "修正内容") → 修正要望、(False, "CANCEL") → キャンセル
        """
        self._target_tools = target_tools
        self._approval_callback = approval_callback

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録。

        BeforeToolCallEventは全ツール呼び出しで発火するため、
        ハンドラー内で対象ツールを必ずフィルタリングすること（R9.8.3参照）。
        """
        registry.add_callback(BeforeToolCallEvent, self._handle_before_tool_call)

    def _handle_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール実行前に承認を求める。"""
        tool_name = event.tool_use["name"] if event.tool_use else ""
        tool_input = event.tool_use["input"] or {} if event.tool_use else {}

        # 対象ツール以外はスキップ
        if tool_name not in self._target_tools:
            return

        # コールバックが設定されている場合はコールバックを使用
        if self._approval_callback is not None:
            approved, message = self._approval_callback(tool_name, tool_input)
            if approved:
                _logger.info("承認コールバック: 承認されました: %s", tool_name)
                return
            elif message == "CANCEL":
                event.cancel_tool = "ユーザーによりキャンセルされました。"
                _logger.info("承認コールバック: キャンセルされました: %s", tool_name)
            else:
                event.cancel_tool = f"修正が指示されました。{message}"
                _logger.info("承認コールバック: 修正が指示されました: %s, 内容: %s", tool_name, message)
            return

        # デフォルト: 対話処理
        self._display_approval_prompt(tool_name, tool_input)
        choice = self._get_user_choice()

        if choice == "1":
            _logger.info("ユーザーが承認しました: %s", tool_name)
            return
        elif choice == "2":
            details = input("修正内容を入力してください: ")
            event.cancel_tool = f"修正が指示されました。{details}"
            _logger.info("ユーザーが修正を指示しました: %s, 内容: %s", tool_name, details)
        else:
            event.cancel_tool = "ユーザーによりキャンセルされました。"
            _logger.info("ユーザーがキャンセルしました: %s", tool_name)

    def _display_approval_prompt(self, tool_name: str, tool_input: dict) -> None:
        """承認プロンプトを表示する。

        Args:
            tool_name: ツール名
            tool_input: ツール入力パラメータ
        """
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📝 申請書を生成します。よろしいですか？")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("[1] OK（申請書を生成する）")
        print("[2] 修正（内容を修正する）")
        print("[3] キャンセル（申請を中止する）")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    def _get_user_choice(self) -> str:
        """ユーザーの選択を取得する。

        Returns:
            ユーザーの選択値（"1", "2", "3"のいずれか）
        """
        while True:
            try:
                choice = input("選択してください [1/2/3]: ").strip()
                if choice in ("1", "2", "3"):
                    return choice
                print("1, 2, 3 のいずれかを入力してください。")
            except (KeyboardInterrupt, EOFError):
                print("\n")
                return "3"
