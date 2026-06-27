"""交通費精算ポリシー

このモジュールは、交通費精算エージェントが使用するルールテキストを提供します。
"""

_TRANSPORTATION_EXPENSE_POLICIES_TEMPLATE = """\
## 交通費精算 業務ルール

### BRL-07: 移動情報の一括収集
- 交通費精算に必要な情報（出発駅、到着駅、利用日、往復/片道、業務目的）について、不足情報はまとめて一括で質問すること
- 1項目ずつ個別に質問してはならない
- ユーザーの負担を最小限にするため、一度の質問で全ての不足情報を収集する

### BRL-08: 交通費の自動計算
- 交通費の金額は calculate_transportation_cost ツールで自動計算すること
- ツールが返却した金額をそのまま申請金額として使用する
- 自動計算できない場合（経路未登録）は、実際にかかった金額をユーザーに確認して使用する

### BRL-09: 申請期限
- 経費発生日から{deadline_months}ヶ月以内に申請すること
- 期限を超過している場合は、期限超過である旨をユーザーに警告する
- 期限超過の申請は受け付けるが、警告メッセージを必ず表示する

### BRL-10: 上長承認
- 交通費合計が{approval_threshold:,}円を超える場合は上長承認が必要
- 上長承認が必要な場合は、その旨をユーザーに通知する

### BRL-11: 駅名の正規化
- ユーザーが入力した駅名の表記ゆれを正規化すること
- 正規化できない駅名の場合は、正しい駅名の確認をユーザーに求める

### BRL-17: 業務目的の必須チェック
- 業務目的が空の場合は警告を表示すること
- 業務目的の入力を促し、未入力のまま申請を完了させない
"""


def get_transportation_expense_policies(deadline_months: int, approval_threshold: int) -> str:
    """交通費精算の業務ルール・ポリシーテキストを返却する。

    Args:
        deadline_months: 申請期限の月数（経費発生日からの期間）
        approval_threshold: 上長承認が必要となる金額閾値（円）

    Returns:
        システムプロンプトに組み込むポリシーテキスト
    """
    return _TRANSPORTATION_EXPENSE_POLICIES_TEMPLATE.format(
        deadline_months=deadline_months,
        approval_threshold=approval_threshold,
    )
