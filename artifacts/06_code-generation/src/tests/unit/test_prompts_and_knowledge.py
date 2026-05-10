"""プロンプトとナレッジの単体テスト"""
from prompt.prompt_orchestrator import ORCHESTRATOR_SYSTEM_PROMPT
from prompt.prompt_transport import get_transport_system_prompt
from prompt.prompt_expense import get_expense_system_prompt
from knowledge.orchestrator_policies import get_orchestrator_policies
from knowledge.transport_policies import get_transport_policies
from knowledge.expense_policies import get_expense_policies


class TestOrchestratorPrompt:
    def test_not_empty(self):
        assert len(ORCHESTRATOR_SYSTEM_PROMPT) > 0

    def test_contains_transport_agent(self):
        assert "transport_agent" in ORCHESTRATOR_SYSTEM_PROMPT

    def test_contains_expense_agent(self):
        assert "expense_agent" in ORCHESTRATOR_SYSTEM_PROMPT

    def test_contains_prohibition(self):
        assert "generate_transport_form" in ORCHESTRATOR_SYSTEM_PROMPT
        assert "generate_expense_form" in ORCHESTRATOR_SYSTEM_PROMPT


class TestTransportPrompt:
    def test_applicant_name_substituted(self):
        prompt = get_transport_system_prompt(
            applicant_name="田中太郎",
            application_date="2026-05-10",
            deadline_date="2026-02-10",
            approval_threshold=10000,
            transport_policies="テストポリシー",
        )
        assert "田中太郎" in prompt

    def test_deadline_date_substituted(self):
        prompt = get_transport_system_prompt(
            applicant_name="田中",
            application_date="2026-05-10",
            deadline_date="2026-02-10",
            approval_threshold=10000,
            transport_policies="テストポリシー",
        )
        assert "2026-02-10" in prompt

    def test_approval_threshold_substituted(self):
        prompt = get_transport_system_prompt(
            applicant_name="田中",
            application_date="2026-05-10",
            deadline_date="2026-02-10",
            approval_threshold=10000,
            transport_policies="テストポリシー",
        )
        assert "10,000" in prompt

    def test_transport_policies_substituted(self):
        prompt = get_transport_system_prompt(
            applicant_name="田中",
            application_date="2026-05-10",
            deadline_date="2026-02-10",
            approval_threshold=10000,
            transport_policies="テストポリシー内容",
        )
        assert "テストポリシー内容" in prompt


class TestExpensePrompt:
    def test_applicant_name_substituted(self):
        prompt = get_expense_system_prompt(
            applicant_name="鈴木花子",
            application_date="2026-05-10",
            deadline_date="2026-02-10",
            approval_threshold=5000,
            expense_policies="テストポリシー",
        )
        assert "鈴木花子" in prompt

    def test_deadline_date_substituted(self):
        prompt = get_expense_system_prompt(
            applicant_name="鈴木",
            application_date="2026-05-10",
            deadline_date="2026-02-10",
            approval_threshold=5000,
            expense_policies="テストポリシー",
        )
        assert "2026-02-10" in prompt

    def test_approval_threshold_substituted(self):
        prompt = get_expense_system_prompt(
            applicant_name="鈴木",
            application_date="2026-05-10",
            deadline_date="2026-02-10",
            approval_threshold=5000,
            expense_policies="テストポリシー",
        )
        assert "5,000" in prompt


class TestKnowledgePolicies:
    def test_orchestrator_policies_not_empty(self):
        """TC-UNIT-060"""
        result = get_orchestrator_policies()
        assert len(result.strip()) > 0

    def test_transport_policies_contains_deadline(self):
        """TC-UNIT-061"""
        result = get_transport_policies(3, 10000)
        assert "3" in result
        assert "10,000" in result

    def test_expense_policies_contains_deadline(self):
        """TC-UNIT-062"""
        result = get_expense_policies(3, 5000)
        assert "3" in result
        assert "5,000" in result
