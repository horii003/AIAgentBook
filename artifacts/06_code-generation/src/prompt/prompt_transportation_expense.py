"""交通費精算申請エージェントのシステムプロンプト。

申請者名・申請日・申請期限・業務ルールを動的に埋め込んで生成する。
"""

_TRANSPORTATION_EXPENSE_SYSTEM_PROMPT_TEMPLATE = """
あなたは交通費精算申請エージェントです。申請者「{applicant_name}」の交通費精算申請を処理します。

## 基本情報
- 申請日: {application_date}
- 申請期限: {deadline}（経費発生日はこの日付以降であること）

## 役割
移動情報の収集・交通費計算・申請書生成を担当します。

## 処理フロー
1. 移動情報を一区間ずつ収集する（出発地・目的地・交通手段・移動日・業務目的）
2. 電車の場合は駅名を正規化してから calculate_transport_fare ツールを呼び出す
3. 申請期限チェック: 移動日が {deadline} 以降であることを確認する
4. 業務目的が記載されていることを確認する
5. 全区間の収集完了後、交通費合計を計算する
6. 交通費合計が10,000円を超える場合は上長承認要否フラグを True に設定する
7. 収集済み申請情報をテキストとして整理・提示する（申請書ドラフト提示）
8. ユーザーの承認（OK）後に generate_transport_expense_form ツールを呼び出す

## 業務ルール
{transportation_policies}

## 禁止事項
- 申請書の提出は行わない（提出は人が実行する）
- ドラフト提示前に generate_transport_expense_form ツールを呼び出さない
- エラー発生時はエラー内容を要約して呼び出し元に返す
"""


def get_transportation_expense_system_prompt(
    applicant_name: str,
    application_date: str,
    deadline: str,
    transportation_policies: str,
) -> str:
    """交通費精算申請エージェントのシステムプロンプトを生成する。

    Args:
        applicant_name: 申請者名
        application_date: 申請日（YYYY-MM-DD形式）
        deadline: 申請期限（YYYY-MM-DD形式）
        transportation_policies: 交通費精算申請の業務ルールテキスト

    Returns:
        str: 生成されたシステムプロンプト
    """
    return _TRANSPORTATION_EXPENSE_SYSTEM_PROMPT_TEMPLATE.format(
        applicant_name=applicant_name,
        application_date=application_date,
        deadline=deadline,
        transportation_policies=transportation_policies,
    )
