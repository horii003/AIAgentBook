"""ポリシー関数の単体テスト"""
from knowledge.transportation_expense_policies import get_transportation_expense_policies
from knowledge.general_expense_policies import get_general_expense_policies


class TestTransportationExpensePolicies:
    """交通費精算ポリシーのテスト"""

    def test_returns_str(self):
        result = get_transportation_expense_policies(3, 10000)
        assert isinstance(result, str)

    def test_contains_deadline_months(self):
        result = get_transportation_expense_policies(3, 10000)
        assert "3ヶ月" in result

    def test_contains_approval_threshold(self):
        result = get_transportation_expense_policies(3, 10000)
        assert "10,000" in result

    def test_different_values(self):
        result = get_transportation_expense_policies(6, 50000)
        assert "6ヶ月" in result
        assert "50,000" in result

    def test_no_placeholders_remaining(self):
        result = get_transportation_expense_policies(3, 10000)
        assert "{" not in result
        assert "}" not in result


class TestGeneralExpensePolicies:
    """一般経費精算ポリシーのテスト"""

    def test_returns_str(self):
        result = get_general_expense_policies(3, 5000)
        assert isinstance(result, str)

    def test_contains_deadline_months(self):
        result = get_general_expense_policies(3, 5000)
        assert "3ヶ月" in result

    def test_contains_approval_threshold(self):
        result = get_general_expense_policies(3, 5000)
        assert "5,000" in result

    def test_different_values(self):
        result = get_general_expense_policies(6, 50000)
        assert "6ヶ月" in result
        assert "50,000" in result

    def test_no_placeholders_remaining(self):
        result = get_general_expense_policies(3, 5000)
        assert "{" not in result
        assert "}" not in result
