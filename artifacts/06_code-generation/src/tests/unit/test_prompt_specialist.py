"""専門エージェントシステムプロンプトの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from prompt.prompt_specialist_expense import get_expense_system_prompt
from prompt.prompt_specialist_transport import get_transport_system_prompt


class TestExpenseSystemPrompt:
    """get_expense_system_prompt のテスト"""

    def _make_prompt(self, **kwargs):
        defaults = dict(
            applicant_name="山田太郎",
            application_date="2026-01-15",
            deadline_date="2025-10-15",
            expense_policies="経費ルール",
            expense_category_policies="区分ルール",
        )
        defaults.update(kwargs)
        return get_expense_system_prompt(**defaults)

    def test_returns_string(self):
        """get_expense_system_prompt() が文字列を返すこと"""
        result = self._make_prompt()
        assert isinstance(result, str)

    def test_contains_applicant_name(self):
        """戻り値に applicant_name が含まれること"""
        result = self._make_prompt(applicant_name="鈴木花子")
        assert "鈴木花子" in result

    def test_contains_application_date(self):
        """戻り値に application_date が含まれること"""
        result = self._make_prompt(application_date="2026-03-01")
        assert "2026-03-01" in result

    def test_no_unfilled_placeholders(self):
        """テンプレートの全プレースホルダーが引数で埋められること（KeyError が発生しないこと）"""
        # KeyError が発生しなければ OK
        result = self._make_prompt()
        assert "{" not in result or "}" not in result or "applicant_name" not in result


class TestTransportSystemPrompt:
    """get_transport_system_prompt のテスト"""

    def _make_prompt(self, **kwargs):
        defaults = dict(
            applicant_name="山田太郎",
            application_date="2026-01-15",
            deadline_date="2025-10-15",
            transport_policies="交通費ルール",
        )
        defaults.update(kwargs)
        return get_transport_system_prompt(**defaults)

    def test_returns_string(self):
        """get_transport_system_prompt() が文字列を返すこと"""
        result = self._make_prompt()
        assert isinstance(result, str)

    def test_contains_applicant_name(self):
        """戻り値に applicant_name が含まれること"""
        result = self._make_prompt(applicant_name="田中次郎")
        assert "田中次郎" in result

    def test_contains_application_date(self):
        """戻り値に application_date が含まれること"""
        result = self._make_prompt(application_date="2026-04-01")
        assert "2026-04-01" in result

    def test_no_unfilled_placeholders(self):
        """テンプレートの全プレースホルダーが引数で埋められること（KeyError が発生しないこと）"""
        result = self._make_prompt()
        assert isinstance(result, str)
