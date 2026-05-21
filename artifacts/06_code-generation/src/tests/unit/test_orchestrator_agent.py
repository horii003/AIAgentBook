"""orchestrator_agent の単体テスト"""
import sys
from unittest.mock import MagicMock, patch

import pytest

# strands モジュールをモックとして登録
if "strands" not in sys.modules:
    mock_strands = MagicMock()
    sys.modules["strands"] = mock_strands
    sys.modules["strands.models"] = mock_strands.models

mock_strands = sys.modules["strands"]
mock_strands.Agent = MagicMock
mock_strands.ModelRetryStrategy = MagicMock
mock_strands.ToolContext = MagicMock
mock_strands.tool = lambda *args, **kwargs: (lambda f: f) if args and callable(args[0]) else (lambda f: f)

# strands.agent.conversation_manager をモック
if "strands.agent.conversation_manager" not in sys.modules:
    mock_conv = MagicMock()
    sys.modules.setdefault("strands.agent", MagicMock())
    sys.modules["strands.agent.conversation_manager"] = mock_conv
    mock_conv.SlidingWindowConversationManager = MagicMock

# strands.hooks をモック
if "strands.hooks" not in sys.modules:
    mock_hooks = MagicMock()
    mock_hooks.HookProvider = type("HookProvider", (), {})
    mock_hooks.HookRegistry = MagicMock
    for event in ["BeforeToolCallEvent", "BeforeInvocationEvent", "AfterInvocationEvent",
                  "BeforeModelCallEvent", "AfterModelCallEvent", "AfterToolCallEvent"]:
        setattr(mock_hooks, event, MagicMock)
    sys.modules["strands.hooks"] = mock_hooks

# strands.session.file_session_manager をモック
if "strands.session.file_session_manager" not in sys.modules:
    mock_fsm = MagicMock()
    sys.modules.setdefault("strands.session", MagicMock())
    sys.modules["strands.session.file_session_manager"] = mock_fsm

# openpyxl をモック
if "openpyxl" not in sys.modules:
    sys.modules["openpyxl"] = MagicMock()

# モジュールをリロード
for mod in list(sys.modules.keys()):
    if mod.startswith(("agents.", "tools.", "handlers.", "session.", "config.", "models.", "prompt.", "knowledge.")):
        del sys.modules[mod]

from agents.orchestrator_agent import OrchestratorAgent
from handlers.error_handler import LoopLimitError


class TestOrchestratorAgentInitialize:
    """OrchestratorAgent._initialize のテスト"""

    def test_initialize_creates_agent(self):
        """_initialize() が Agent インスタンスを生成すること"""
        agent = OrchestratorAgent()
        with patch("builtins.input", return_value="山田太郎"):
            with patch("os.makedirs"):
                agent._initialize()
        assert agent.agent is not None

    def test_initialize_sets_user_name(self):
        """_initialize() が申請者名を設定すること"""
        agent = OrchestratorAgent()
        with patch("builtins.input", return_value="鈴木花子"):
            with patch("os.makedirs"):
                agent._initialize()
        assert agent._user_name == "鈴木花子"

    def test_initialize_sets_session_id(self):
        """_initialize() がセッションIDを設定すること"""
        agent = OrchestratorAgent()
        with patch("builtins.input", return_value="山田太郎"):
            with patch("os.makedirs"):
                agent._initialize()
        assert agent._session_id != ""


class TestOrchestratorAgentRun:
    """OrchestratorAgent.run のテスト"""

    def test_run_exits_on_quit(self):
        """'quit' 入力時にループが終了すること"""
        agent = OrchestratorAgent()
        with patch("builtins.input", side_effect=["山田太郎", "quit"]):
            with patch("os.makedirs"):
                agent.run()  # 例外なく終了すること

    def test_run_exits_on_exit(self):
        """'exit' 入力時にループが終了すること"""
        agent = OrchestratorAgent()
        with patch("builtins.input", side_effect=["山田太郎", "exit"]):
            with patch("os.makedirs"):
                agent.run()

    def test_invocation_state_built_correctly(self):
        """InvocationState が正しく構築されること"""
        from models.data_models import InvocationState
        state = InvocationState(
            user_name="山田太郎",
            request_date="2026-05-21",
            session_id="test_session",
        )
        assert state.user_name == "山田太郎"
        assert state.request_date == "2026-05-21"
        assert state.session_id == "test_session"
