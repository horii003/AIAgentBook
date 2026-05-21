"""prompt_transportation_expense の単体テスト"""
from prompt.prompt_transportation_expense import get_transportation_expense_system_prompt


class TestGetTransportationExpenseSystemPrompt:
    """get_transportation_expense_system_prompt のテスト"""

    def test_returns_string(self):
        """文字列を返すこと"""
        result = get_transportation_expense_system_prompt(
            applicant_name="山田太郎",
            application_date="2026-05-21",
            deadline="2026-02-21",
            transportation_policies="テストポリシー",
        )
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_contains_applicant_name(self):
        """申請者名がプロンプトに反映されること"""
        result = get_transportation_expense_system_prompt(
            applicant_name="鈴木花子",
            application_date="2026-05-21",
            deadline="2026-02-21",
            transportation_policies="テストポリシー",
        )
        assert "鈴木花子" in result

    def test_contains_application_date(self):
        """申請日がプロンプトに反映されること"""
        result = get_transportation_expense_system_prompt(
            applicant_name="山田太郎",
            application_date="2026-05-21",
            deadline="2026-02-21",
            transportation_policies="テストポリシー",
        )
        assert "2026-05-21" in result

    def test_contains_deadline(self):
        """申請期限がプロンプトに反映されること"""
        result = get_transportation_expense_system_prompt(
            applicant_name="山田太郎",
            application_date="2026-05-21",
            deadline="2026-02-21",
            transportation_policies="テストポリシー",
        )
        assert "2026-02-21" in result

    def test_contains_transportation_policies(self):
        """transportation_policies の内容が含まれること"""
        result = get_transportation_expense_system_prompt(
            applicant_name="山田太郎",
            application_date="2026-05-21",
            deadline="2026-02-21",
            transportation_policies="カスタムポリシーテキスト",
        )
        assert "カスタムポリシーテキスト" in result
