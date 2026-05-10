"""経費精算申請ルール（KN-003）

このモジュールは、経費精算申請エージェント（AG-003）が使用するルールテキストを提供します。
"""


def get_expense_policies(deadline_months: int, approval_threshold: int) -> str:
    """経費精算申請ルールのテキストを返す。

    Args:
        deadline_months: 申請期限（月数）
        approval_threshold: 上長承認が必要な経費合計の閾値（円）

    Returns:
        str: ルールのテキスト（マークダウン形式）
    """
    return f"""
- BRL-10: 経費精算申請書を使用する
- BRL-11: 申請先は経理部門
- BRL-12: 対応経費区分は事務用品費・宿泊費・資格精算費・その他経費のみ
- BRL-13: 領収書画像からの自動抽出（要件上未定義）
- BRL-14: 経費区分は品目から自動判断するが、必ずユーザーへ確認を求める（自動確定禁止）
- BRL-15: 申請期限は経費発生日から{deadline_months}ヶ月以内
- BRL-16: 経費合計が{approval_threshold:,}円を超える場合は上長承認が必要であることを通知する
- BRL-17: 業務目的は必須
"""
