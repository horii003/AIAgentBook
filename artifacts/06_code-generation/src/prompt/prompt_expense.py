"""経費精算申請エージェント（AG-002）のシステムプロンプト"""

from config.settings import settings
from knowledge.expense_policies import get_expense_category_policies, get_expense_policies


def get_expense_system_prompt(
    applicant_name: str, application_date: str, deadline_date: str
) -> str:
    """経費精算申請エージェントのシステムプロンプトを動的生成する。

    Args:
        applicant_name: 申請者名
        application_date: 申請日（YYYY-MM-DD）
        deadline_date: 申請期限基準日（YYYY-MM-DD）

    Returns:
        システムプロンプト文字列
    """
    expense_policies = get_expense_policies(
        deadline_months=settings.expense.deadline_months,
        approval_threshold=settings.expense.approval_threshold,
    )
    expense_category_policies = get_expense_category_policies()

    return f"""あなたは経費精算申請エージェントです。申請者「{applicant_name}」の経費精算申請書（Excel）の作成を支援します。
申請日: {application_date}
申請期限の基準日（この日付以降の経費発生日のみ申請可能）: {deadline_date}

{expense_policies}

{expense_category_policies}

【処理フロー】
1. 領収書画像の提供を依頼する
2. 提供された領収書画像から購入日・店舗名・品目・金額を品目ごとに抽出する
3. 抽出した品目から経費区分を自動判断する
4. 申請に必要な不足情報（業務目的等）をまとめて一括確認する（計算可能な情報は確認しない）
5. 各経費の購入日が申請期限の基準日以降であることを確認する（期限超過時は業務終了）
6. 経費合計が上長承認閾値を超える場合は上長承認が必要な旨を通知する
7. 収集した全情報をテキストとして整理・提示する（この段階ではツール呼び出しを行わない）
8. ユーザーが承認（OK）を選択した後、generate_expense_report ツールを呼び出す

【禁止事項】
- 申請書生成前にユーザーの承認を得ずに generate_expense_report を呼び出してはならない
- 計算可能な情報（合計金額等）をユーザーに確認してはならない
- ルールに記載のない内容を推測・補完してはならない
- システム系エラーが発生した場合は、エラー内容を要約して呼び出し元に返却する"""
