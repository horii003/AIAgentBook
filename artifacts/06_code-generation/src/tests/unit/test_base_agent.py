"""エージェント共通ユーティリティの単体テスト"""

from agents.base_agent import calculate_deadline


class TestCalculateDeadline:
    """calculate_deadline のテスト"""

    def test_normal(self):
        """正しい期限日を返すこと"""
        result = calculate_deadline("2026-05-17", 3)
        assert result == "2026-02-17"

    def test_year_boundary(self):
        """年をまたぐ場合"""
        result = calculate_deadline("2026-02-15", 3)
        assert result == "2025-11-15"

    def test_invalid_date(self):
        """不正な日付文字列で '要確認' を返すこと"""
        result = calculate_deadline("invalid", 3)
        assert result == "要確認"

    def test_empty_date(self):
        """空文字列で '要確認' を返すこと"""
        result = calculate_deadline("", 3)
        assert result == "要確認"
