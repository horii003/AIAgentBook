"""receipt_policies の単体テスト"""
from knowledge.receipt_policies import get_receipt_policies


class TestGetReceiptPolicies:
    """get_receipt_policies のテスト"""

    def test_returns_string(self):
        """文字列を返すこと"""
        result = get_receipt_policies(deadline_months=3, approval_threshold=5000)
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_contains_deadline_months(self):
        """deadline_months の値がルールテキストに反映されること"""
        result = get_receipt_policies(deadline_months=6, approval_threshold=5000)
        assert "6" in result

    def test_contains_approval_threshold(self):
        """approval_threshold の値がルールテキストに反映されること"""
        result = get_receipt_policies(deadline_months=3, approval_threshold=10000)
        assert "10,000" in result or "10000" in result

    def test_different_values_reflected(self):
        """異なる設定値が正しく反映されること"""
        result1 = get_receipt_policies(deadline_months=3, approval_threshold=5000)
        result2 = get_receipt_policies(deadline_months=6, approval_threshold=10000)
        assert result1 != result2
