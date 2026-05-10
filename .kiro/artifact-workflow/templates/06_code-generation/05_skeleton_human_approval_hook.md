# スケルトン: Human-in-the-Loop承認フック (handlers/human_approval_hook.md)

## 概要

出力生成等の重要なツール実行前に人間の承認を求めるフック。
承認対象のツール名を業務ドメインに応じて設定する。

Hook（制御点）と UI処理を分離するアーキテクチャを採用しており、
UIとのやりとりは呼び出し元から注入された `approval_callback` が担当する。

## ファイル配置

`handlers/human_approval_hook.py`

## スケルトンコード

```python
"""
Human-in-the-Loop承認フック

{対象ツール名}の実行前に人間の承認を求め、
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
from strands.hooks import HookProvider, HookRegistry, BeforeToolCallEvent

_logger = logging.getLogger(__name__)


class HumanApprovalHook(HookProvider):
    """指定ツール実行前に人間の承認を求めるフック。

    Hookは制御点として機能し、UI入力は呼び出し元から注入された approval_callback に委譲する。
    """

    # TODO: 承認対象のツール名を業務ドメインに応じて設定する
    APPROVAL_REQUIRED_TOOLS: frozenset[str] = frozenset({
        "{tool_name_a}",
        "{tool_name_b}",
    })

    def __init__(
        self,
        approval_callback: Callable[[str, dict], tuple],
        approval_required_tools: Optional[list[str]] = None,
    ):
        """
        初期化

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
        self.approval_callback = approval_callback
        self.approval_required_tools: frozenset[str] = (
            frozenset(approval_required_tools)
            if approval_required_tools is not None
            else self.APPROVAL_REQUIRED_TOOLS
        )

    def register_hooks(self, registry: HookRegistry, **kwargs: Any) -> None:
        """フックの登録。

        BeforeToolCallEventは全ツール呼び出しで発火するため、
        ハンドラー内で対象ツールを必ずフィルタリングすること（R9.8.3参照）。
        """
        registry.add_callback(BeforeToolCallEvent, self._on_before_tool_call)

    def _on_before_tool_call(self, event: BeforeToolCallEvent) -> None:
        """ツール実行前に承認を求める。"""
        # TODO: 詳細設計書に従い実装
        # - ツール名・入力パラメータの取得（R9.8.3参照）
        #   tool_name = event.tool_use.get("name", "") if event.tool_use else ""
        #   tool_params = event.tool_use.get("input", {}) if event.tool_use else {}
        # - approval_required_tools に含まれないツールはreturnでスキップ
        # - ログ出力（_logger.info）
        # - approval_callbackを呼び出し (approved, feedback) を受け取る
        # - approved=Trueの場合: ログ出力してreturn（ツールがそのまま実行される）
        # - approved=Falseの場合: _build_cancel_message()でメッセージを生成し
        #   event.cancel_tool に設定してキャンセル（event.cancel()は存在しない）
        pass

    def _build_cancel_message(self, tool_name: str, feedback: str) -> str:
        """
        キャンセルメッセージを生成する。

        event.cancel_toolに設定した文字列はツール結果としてLLMに返却される。
        LLMへの指示として機能するため、次のアクションを明示的に記述すること。

        Args:
            tool_name: ツール名
            feedback: ユーザーからのフィードバック（"CANCEL"=拒否、それ以外=修正要望、空=拒否）

        Returns:
            str: LLMへ返却するキャンセルメッセージ
        """
        # TODO: 詳細設計書に従い実装
        # - feedbackが"CANCEL"または空の場合: 申請中止メッセージを返す
        # - feedbackに修正内容がある場合: 修正要望をLLMに伝えて再生成を促すメッセージを返す
        pass
```

## カスタマイズガイド

1. **承認対象ツール**: `APPROVAL_REQUIRED_TOOLS` に業務ドメインの出力生成ツール名を設定する。`BeforeToolCallEvent` は全ツール呼び出しで発火するため、対象外ツールは必ず `return` でスキップすること
2. **承認コールバック**: コンソール以外のUI（Web、Slack等）で承認を受ける場合、カスタムコールバックを `approval_callback` に渡す
3. **キャンセルメッセージ**: `event.cancel_tool` に設定した文字列がツール結果としてLLMに返却される。LLMへの指示として機能するため、次のアクションを明示的に記述する
