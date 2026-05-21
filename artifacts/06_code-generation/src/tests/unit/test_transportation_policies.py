"""transportation_policies の単体テスト"""
from knowledge.transportation_policies import get_transportation_policies


class TestGetTransportationPolicies:
    """get_transportation_policies のテスト"""

    def test_returns_string(self):
        """文字列を返すこと"""
        result = get_transportation_policies(deadline_months=3, approval_threshold=10000)
        assert isinstance(result, str)
        assert len(result.strip()) > 0

    def test_contains_deadline_months(self):
        """deadline_months の値がルールテキストに反映されること"""
        result = get_transportation_policies(deadline_months=6, approval_threshold=10000)
        assert "6" in result

    def test_contains_approval_threshold(self):
        """approval_threshold の値がルールテキストに反映されること"""
        result = get_transportation_policies(deadline_months=3, approval_threshold=20000)
        assert "20,000" in result or "20000" in result

    def test_different_values_reflected(self):
        """異なる設定値が正しく反映されること"""
        result1 = get_transportation_policies(deadline_months=3, approval_threshold=10000)
        result2 = get_transportation_policies(deadline_months=6, approval_threshold=20000)
        assert result1 != result2
