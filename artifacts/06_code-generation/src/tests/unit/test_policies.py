"""ナレッジ・業務ルールの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from knowledge.application_policies import get_application_policies
from knowledge.transport_policies import get_transport_policies
from knowledge.expense_policies import get_expense_policies, get_expense_category_policies


class TestApplicationPolicies:
    """application_policies のテスト"""

    def test_returns_string(self):
        """get_application_policies() が文字列を返すこと"""
        result = get_application_policies()
        assert isinstance(result, str)

    def test_not_empty(self):
        """空文字を返さないこと"""
        result = get_application_policies()
        assert len(result.strip()) > 0


class TestTransportPolicies:
    """transport_policies のテスト"""

    def test_returns_string(self):
        """get_transport_policies() が文字列を返すこと"""
        result = get_transport_policies(3, 10000)
        assert isinstance(result, str)

    def test_contains_deadline_months(self):
        """戻り値に deadline_months の値が含まれること"""
        result = get_transport_policies(3, 10000)
        assert "3" in result

    def test_contains_approval_threshold(self):
        """戻り値に approval_threshold の値が含まれること（カンマ区切り）"""
        result = get_transport_policies(3, 10000)
        assert "10,000" in result

    def test_not_empty(self):
        """空文字を返さないこと"""
        result = get_transport_policies(3, 10000)
        assert len(result.strip()) > 0


class TestExpensePolicies:
    """expense_policies のテスト"""

    def test_get_expense_policies_returns_string(self):
        """get_expense_policies() が文字列を返すこと"""
        result = get_expense_policies(3, 5000)
        assert isinstance(result, str)

    def test_contains_deadline_months(self):
        """戻り値に deadline_months の値が含まれること"""
        result = get_expense_policies(3, 5000)
        assert "3" in result

    def test_contains_approval_threshold(self):
        """戻り値に approval_threshold の値が含まれること（カンマ区切り）"""
        result = get_expense_policies(3, 5000)
        assert "5,000" in result

    def test_not_empty(self):
        """空文字を返さないこと"""
        result = get_expense_policies(3, 5000)
        assert len(result.strip()) > 0

    def test_get_expense_category_policies_returns_string(self):
        """get_expense_category_policies() が文字列を返すこと"""
        result = get_expense_category_policies()
        assert isinstance(result, str)

    def test_contains_four_categories(self):
        """戻り値に4つの経費区分が含まれること"""
        result = get_expense_category_policies()
        assert "事務用品費" in result
        assert "宿泊費" in result
        assert "資格精算費" in result
        assert "その他経費" in result

    def test_category_not_empty(self):
        """空文字を返さないこと"""
        result = get_expense_category_policies()
        assert len(result.strip()) > 0
