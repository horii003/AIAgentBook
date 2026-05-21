"""交通費精算申請の業務ルール・ポリシー。

ビジネスルール値は引数で受け取り動的展開する（ハードコード禁止）。
他モジュールへの依存なし（純粋なテキスト返却）。
"""


def get_transportation_policies(deadline_months: int, approval_threshold: int) -> str:
    """交通費精算申請の業務ルールテキストを返す。

    Args:
        deadline_months: 申請期限（経費発生日からの月数）
        approval_threshold: 上長承認が必要な交通費合計閾値（円）

    Returns:
        str: 業務ルールテキスト（マークダウン形式）
    """
    return f"""
- BRL-07: 移動情報は一区間ずつ収集する（出発地・目的地・交通手段・移動日・業務目的）
- BRL-08: 運賃は calculate_transport_fare ツールで自動計算する
- BRL-09: 申請期限は経費発生日から{deadline_months}ヶ月以内。超過時は申請不可を案内して処理を終了する
- BRL-10: 交通費合計が{approval_threshold:,}円を超える場合は上長承認欄を追加する（needs_approval=True）
- BRL-11: 電車の場合は駅名を正規化してから calculate_transport_fare ツールに渡す
- BRL-12: 業務目的は必須。未記載時は入力を促す
"""
