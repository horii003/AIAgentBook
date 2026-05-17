"""ナレッジ・業務ルールの単体テスト"""

from knowledge.application_policies import get_application_policies
from knowledge.expense_policies import get_expense_category_policies, get_expense_policies
from knowledge.transport_policies import get_transport_policies


class TestApplicationPolicies:
    """get_application_policies のテスト"""

    def test_returns_non_empty(self):
        result = get_application_policies()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_brl_keywords(self):
        result = get_application_policies()
        assert "BRL-01" in result
        assert "BRL-02" in result
        assert "BRL-03" in result
        assert "BRL-05" in result
        assert "transport_agent" in result
        assert "expense_agent" in result


class TestTransportPolicies:
    """get_transport_policies のテスト"""

    def test_returns_non_empty(self):
        result = get_transport_policies(deadline_months=3, approval_threshold=10000)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_dynamic_values(self):
        result = get_transport_policies(deadline_months=6, approval_threshold=20000)
        assert "6ヶ月" in result
        assert "20,000円" in result

    def test_contains_brl_keywords(self):
        result = get_transport_policies(deadline_months=3, approval_threshold=10000)
        assert "BRL-08" in result
        assert "BRL-10" in result
        assert "BRL-12" in result


class TestExpensePolicies:
    """get_expense_policies のテスト"""

    def test_returns_non_empty(self):
        result = get_expense_policies(deadline_months=3, approval_threshold=10000)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_dynamic_values(self):
        result = get_expense_policies(deadline_months=6, approval_threshold=50000)
        assert "6ヶ月" in result
        assert "50,000円" in result

    def test_contains_brl_keywords(self):
        result = get_expense_policies(deadline_months=3, approval_threshold=10000)
        assert "BRL-09" in result
        assert "BRL-11" in result


class TestExpenseCategoryPolicies:
    """get_expense_category_policies のテスト"""

    def test_returns_non_empty(self):
        result = get_expense_category_policies()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_categories(self):
        result = get_expense_category_policies()
        assert "事務用品費" in result
        assert "宿泊費" in result
        assert "資格精算費" in result
        assert "その他経費" in result
