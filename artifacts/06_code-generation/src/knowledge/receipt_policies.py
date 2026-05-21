"""経費精算申請の業務ルール・ポリシー。

ビジネスルール値は引数で受け取り動的展開する（ハードコード禁止）。
他モジュールへの依存なし（純粋なテキスト返却）。
"""


def get_receipt_policies(deadline_months: int, approval_threshold: int) -> str:
    """経費精算申請の業務ルールテキストを返す。

    Args:
        deadline_months: 申請期限（経費発生日からの月数）
        approval_threshold: 上長承認が必要な経費合計閾値（円）

    Returns:
        str: 業務ルールテキスト（マークダウン形式）
    """
    return f"""
- BRL-12: 業務目的は必須。未記載時は入力を促す
- BRL-13: 領収書画像から購入日・店舗名・品目・金額を自動抽出する。失敗時は手動入力を促す
- BRL-14: 品目から経費区分を自動判断する（事務用品費・宿泊費・資格精算費・その他経費）。判断不能時はユーザーに選択肢を提示する
- BRL-15: 申請期限は経費発生日から{deadline_months}ヶ月以内。超過時は申請不可を案内して処理を終了する
- BRL-16: 経費合計が{approval_threshold:,}円を超える場合は上長承認欄を追加する（needs_approval=True）
"""
