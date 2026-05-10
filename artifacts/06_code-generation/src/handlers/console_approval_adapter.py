"""コンソール承認アダプター

HumanApprovalHookに注入するCLI用の承認コールバック関数を提供する。
"""


def console_approval_callback(tool_name: str, tool_params: dict) -> tuple[bool, str]:
    """コンソール入力で承認を求めるコールバック関数。

    Args:
        tool_name: 呼び出されるツール名
        tool_params: ツールへの入力パラメータ

    Returns:
        tuple[bool, str]:
            (True, "")         : 承認
            (False, "CANCEL")  : キャンセル
            (False, "修正内容") : 修正要望
    """
    print("\n申請書を生成してよろしいですか？")
    print("[1] OK（承認）")
    print("[2] 修正要望")
    print("[3] キャンセル")
    choice = input("選択してください（1/2/3）: ").strip()
    if choice == "1":
        return (True, "")
    elif choice == "2":
        revision = input("修正内容を入力してください: ").strip()
        return (False, revision if revision else "修正要望が選択されました。申請内容を修正してください。")
    else:
        return (False, "CANCEL")
