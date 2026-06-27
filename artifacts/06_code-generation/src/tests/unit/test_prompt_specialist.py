"""専門エージェントプロンプトの単体テスト"""
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from prompt.prompt_transportation_expense import get_transportation_expense_system_prompt
from prompt.prompt_general_expense import get_general_expense_system_prompt


class TestOrchestratorPrompt:
    """オーケストレータープロンプトのテスト"""

    def test_is_str(self):
        assert isinstance(ORCHESTRATOR_SYSTEM_PROMPT, str)

    def test_not_empty(self):
        assert len(ORCHESTRATOR_SYSTEM_PROMPT) > 0

    def test_contains_jd_keywords(self):
        assert "JD-01" in ORCHESTRATOR_SYSTEM_PROMPT
        assert "JD-02" in ORCHESTRATOR_SYSTEM_PROMPT
        assert "JD-03" in ORCHESTRATOR_SYSTEM_PROMPT


class TestTransportationExpensePrompt:
    """交通費精算プロンプトのテスト"""

    def test_returns_str(self):
        result = get_transportation_expense_system_prompt(
            applicant_name="山田太郎",
            application_date="2026-05-23",
            deadline="2026-02-23",
        )
        assert isinstance(result, str)

    def test_no_placeholders_remaining(self):
        result = get_transportation_expense_system_prompt(
            applicant_name="山田太郎",
            application_date="2026-05-23",
            deadline="2026-02-23",
        )
        # 未展開のプレースホルダーがないこと
        import re
        placeholders = re.findall(r"\{[a-z_]+\}", result)
        assert len(placeholders) == 0, f"未展開プレースホルダー: {placeholders}"

    def test_contains_applicant_name(self):
        result = get_transportation_expense_system_prompt(
            applicant_name="山田太郎",
            application_date="2026-05-23",
            deadline="2026-02-23",
        )
        assert "山田太郎" in result


class TestGeneralExpensePrompt:
    """経費精算プロンプトのテスト"""

    def test_returns_str(self):
        result = get_general_expense_system_prompt(
            applicant_name="鈴木花子",
            application_date="2026-05-23",
            deadline="2026-02-23",
        )
        assert isinstance(result, str)

    def test_no_placeholders_remaining(self):
        result = get_general_expense_system_prompt(
            applicant_name="鈴木花子",
            application_date="2026-05-23",
            deadline="2026-02-23",
        )
        import re
        placeholders = re.findall(r"\{[a-z_]+\}", result)
        assert len(placeholders) == 0, f"未展開プレースホルダー: {placeholders}"

    def test_contains_applicant_name(self):
        result = get_general_expense_system_prompt(
            applicant_name="鈴木花子",
            application_date="2026-05-23",
            deadline="2026-02-23",
        )
        assert "鈴木花子" in result
