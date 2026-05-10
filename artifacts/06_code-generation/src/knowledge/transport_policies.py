"""交通費精算申請ルール（KN-002）

このモジュールは、交通費精算申請エージェント（AG-002）が使用するルールテキストを提供します。
"""


def get_transport_policies(deadline_months: int, approval_threshold: int) -> str:
    """交通費精算申請ルールのテキストを返す。

    Args:
        deadline_months: 申請期限（月数）
        approval_threshold: 上長承認が必要な交通費合計の閾値（円）

    Returns:
        str: ルールのテキスト（マークダウン形式）
    """
    return f"""
- BRL-01: 交通費精算申請書を使用する
- BRL-02: 申請先は経理部門
- BRL-03: 対応交通手段は電車・バス・タクシー・飛行機のみ
- BRL-04: 移動情報は1区間ずつ収集する
- BRL-05: 経路テーブルを参照して交通費を自動計算する（未登録時は手動入力）
- BRL-06: 申請期限は経費発生日から{deadline_months}ヶ月以内
- BRL-07: 交通費合計が{approval_threshold:,}円を超える場合は上長承認が必要であることを通知する
- BRL-08: 出発地・目的地の「駅」「バス停」「空港」等の接尾語は自動除去して正規化する
- BRL-09: 業務目的は必須
"""
