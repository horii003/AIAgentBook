"""一般経費精算ポリシー

このモジュールは、経費精算エージェントが使用するルールテキストを提供します。
"""

_GENERAL_EXPENSE_POLICIES_TEMPLATE = """\
## 一般経費精算 業務ルール

### BRL-13: 領収書情報の抽出
- 領収書画像から店舗名・品目・金額・日付を抽出すること
- 抽出結果はユーザーに確認を求め、誤りがあれば修正を受け付ける
- 画像が不鮮明で読み取れない場合は、手動入力を促す

### BRL-14: 経費区分の自動判断
- 品目名から経費区分を自動判断すること
- 判断結果はユーザーに提示し、変更があれば受け付ける
- 判断できない品目の場合は、経費区分の選択をユーザーに求める

### BRL-15: 申請期限
- 経費発生日から{deadline_months}ヶ月以内に申請すること
- 期限を超過している場合は、期限超過である旨をユーザーに警告する
- 期限超過の申請は受け付けるが、警告メッセージを必ず表示する

### BRL-16: 上長承認
- 経費合計が{approval_threshold:,}円を超える場合は上長承認が必要
- 上長承認が必要な場合は、その旨をユーザーに通知する

### BRL-17: 業務目的の必須チェック
- 業務目的が空の場合は警告を表示すること
- 業務目的の入力を促し、未入力のまま申請を完了させない
"""


def get_general_expense_policies(deadline_months: int, approval_threshold: int) -> str:
    """一般経費精算の業務ルール・ポリシーテキストを返却する。

    Args:
        deadline_months: 申請期限の月数（経費発生日からの期間）
        approval_threshold: 上長承認が必要となる金額閾値（円）

    Returns:
        システムプロンプトに組み込むポリシーテキスト
    """
    return _GENERAL_EXPENSE_POLICIES_TEMPLATE.format(
        deadline_months=deadline_months,
        approval_threshold=approval_threshold,
    )
