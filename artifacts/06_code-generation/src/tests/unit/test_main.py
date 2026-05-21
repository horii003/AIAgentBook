"""main.py の単体テスト"""
import os
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

# 必要なモジュールをモック
for mod_name, mock_obj in [
    ("strands.agent", MagicMock()),
    ("strands.agent.conversation_manager", MagicMock()),
    ("strands.hooks", MagicMock()),
    ("strands.session", MagicMock()),
    ("strands.session.file_session_manager", MagicMock()),
    ("openpyxl", MagicMock()),
]:
    sys.modules.setdefault(mod_name, mock_obj)

if not hasattr(sys.modules["strands.agent.conversation_manager"], "SlidingWindowConversationManager"):
    sys.modules["strands.agent.conversation_manager"].SlidingWindowConversationManager = MagicMock

hooks_mod = sys.modules["strands.hooks"]
if not hasattr(hooks_mod, "HookProvider"):
    hooks_mod.HookProvider = type("HookProvider", (), {})
    for event in ["BeforeToolCallEvent", "BeforeInvocationEvent", "AfterInvocationEvent",
                  "BeforeModelCallEvent", "AfterModelCallEvent", "AfterToolCallEvent"]:
        setattr(hooks_mod, event, MagicMock)

# モジュールをリロード
for mod in list(sys.modules.keys()):
    if mod.startswith(("agents.", "tools.", "handlers.", "session.", "config.", "models.", "prompt.", "knowledge.")):
        del sys.modules[mod]
if "main" in sys.modules:
    del sys.modules["main"]

# logsディレクトリを作成してからmainをインポート
os.makedirs("logs", exist_ok=True)
import main


class TestMain:
    """main.py のテスト"""

    def test_main_normal_exit(self):
        """main() が正常終了すること（OrchestratorAgent.run() モック）"""
        with patch.object(main, "OrchestratorAgent") as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent_class.return_value = mock_agent
            main.main()
            mock_agent.run.assert_called_once()

    def test_main_keyboard_interrupt(self):
        """KeyboardInterrupt 発生時の処理確認"""
        with patch.object(main, "OrchestratorAgent") as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.run.side_effect = KeyboardInterrupt()
            mock_agent_class.return_value = mock_agent
            # KeyboardInterrupt は sys.exit を呼ばずに終了すること
            main.main()

    def test_main_exception_exits_with_1(self):
        """Exception 発生時に sys.exit(1) が呼ばれること"""
        with patch.object(main, "OrchestratorAgent") as mock_agent_class:
            mock_agent = MagicMock()
            mock_agent.run.side_effect = Exception("テストエラー")
            mock_agent_class.return_value = mock_agent
            with pytest.raises(SystemExit) as exc_info:
                main.main()
            assert exc_info.value.code == 1
