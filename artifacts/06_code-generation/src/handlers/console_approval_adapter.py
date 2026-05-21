"""コンソール承認アダプター。

HumanApprovalHook に注入するコンソールベースの承認コールバック関数を提供する。
ユーザーとのインタラクション（print/input）を担当する。
"""
import json
import logging

_logger = logging.getLogger(__name__)


def console_approval_callback(tool_name: str, tool_params: dict) -> tuple:
    """コンソールでユーザーに承認を求めるコールバック関数。

    申請内容を表示し、承認・修正・キャンセルの選択を受け付ける。

    Args:
        tool_name: 呼び出されるツール名
        tool_params: ツールへの入力パラメータ

    Returns:
        tuple: (approved: bool, feedback: str)
            (True, "")         : 承認
            (False, "CANCEL")  : キャンセル
            (False, "修正内容"): 修正要望
    """
    print("\n" + "=" * 60)
    print("【申請書生成の確認】")
    print(f"ツール: {tool_name}")
    print("申請内容:")
    try:
        print(json.dumps(tool_params, ensure_ascii=False, indent=2))
    except Exception:
        print(str(tool_params))
    print("=" * 60)
    print("以下から選択してください:")
    print("  1. 承認（このまま申請書を生成する）")
    print("  2. 修正（修正内容を入力する）")
    print("  3. キャンセル（申請書生成を中止する）")

    while True:
        choice = input("\n選択 [1/2/3]: ").strip()

        if choice == "1":
            _logger.info("申請書生成承認: tool_name=%s", tool_name)
            return (True, "")

        elif choice == "2":
            feedback = input("修正内容を入力してください: ").strip()
            if feedback:
                _logger.info("申請書生成修正要望: tool_name=%s", tool_name)
                return (False, feedback)
            else:
                print("修正内容を入力してください。")

        elif choice == "3":
            _logger.info("申請書生成キャンセル: tool_name=%s", tool_name)
            return (False, "CANCEL")

        else:
            print("1、2、または3を入力してください。")
