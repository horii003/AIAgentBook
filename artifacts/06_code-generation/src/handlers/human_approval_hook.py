"""Human-in-the-Loop承認フック。

申請書生成ツールの実行前に人間の承認を求め、
修正要望があれば修正を実行するフック。

【2層承認構造について】
本システムの承認フローは意図的に2段階になっている:

  1. プロンプト層（専門エージェントのsystem_prompt）:
     LLMが申請内容の下書きをユーザーに見せ、「OK/修正/キャンセル」を対話で確認する。
     これはLLMが収集した情報が正しいかをユーザーが「見て確認」するためのステップ。

  2. フック層（このクラス: BeforeToolCallEvent）:
     ツール実行の直前にSDKフックで割り込み、再度承認を求める。
     プロンプトへの指示だけではLLMの動作を100%保証できないため、
     コード側で「ツールを実際に動かす前に必ず人間が確認する」ことを保証する安全装置。

【責務の分離】
  このクラス（HumanApprovalHook）: 承認が必要なタイミングを検知する制御点のみ担当。
  UIとのやりとり（print/input）は呼び出し元から注入された approval_callback が担当する。
  CLIからWebやSlackに変更する場合もこのクラスを変更せずコールバックのみ差し替えられる。
"""
import logging
from typing import Any, Callable, Optional

from strands.hooks import BeforeToolCallEvent, HookProvider, HookRegistry

_logger = logging.getLogger(__name__)


class HumanApprovalHook(HookProvider):
    """指定ツール実行前に人間の承認を求めるフック。

    Hookは制御点として機能し、UI入力は呼び出し元から注入された approval_callback に委譲する。
    """

    # 承認対象のツール名（申請書生成ツール）
    APPROVAL_REQUIRED_TOOLS: frozenset = frozenset({
        "generate_transport_expense_form",
        "generate_general_expense_form",
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
                               Noneの場合はデフォルト（APPROVAL_REQUIRED_TOOLS）を使用。
        """
        self._approval_callback = approval_callback
        self._target_tools: frozenset = (
            frozenset(approval_required_tools)
            if approval_required_tools is not None
            else self.APPROVAL_REQUIRED_TOOLS
        )

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックを登録する。

        BeforeToolCallEventは全ツール呼び出しで発火するため、
        ハンドラー内で対象ツールを必ずフィルタリングすること（R9.8.3参照）。

        Args:
            registry: フックレジストリ
        """
        registry.add_callback(BeforeToolCallEvent, self._on_before_tool_call)

    def _on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール実行前に承認を求める。

        Args:
            event: BeforeToolCallEvent
        """
        # ツール名・入力パラメータの取得
        tool_name = event.tool_use["name"] if event.tool_use else "unknown"
        tool_params = (event.tool_use.get("input") or {}) if event.tool_use else {}

        # 対象外ツールはスキップ
        if tool_name not in self._target_tools:
            return

        _logger.info("申請書生成承認確認: tool_name=%s", tool_name)

        # 承認コールバックを呼び出す
        approved, feedback = self._approval_callback(tool_name, tool_params)

        if approved:
            _logger.info("申請書生成承認: tool_name=%s", tool_name)
            return

        # キャンセルまたは修正要望
        cancel_message = self._build_cancel_message(tool_name, feedback)
        event.cancel_tool = cancel_message

        if feedback == "CANCEL":
            _logger.info("申請書生成キャンセル: tool_name=%s", tool_name)
        else:
            _logger.info("申請書生成修正要望: tool_name=%s", tool_name)

    def _build_cancel_message(self, tool_name: str, feedback: str) -> str:
        """キャンセルメッセージを生成する。

        event.cancel_toolに設定した文字列はツール結果としてLLMに返却される。
        LLMへの指示として機能するため、次のアクションを明示的に記述すること。

        Args:
            tool_name: ツール名
            feedback: ユーザーからのフィードバック（"CANCEL"=拒否、それ以外=修正要望、空=拒否）

        Returns:
            str: LLMへ返却するキャンセルメッセージ
        """
        if not feedback or feedback == "CANCEL":
            return "申請書生成をキャンセルしました。"
        return feedback
