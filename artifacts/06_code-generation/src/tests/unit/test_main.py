"""メインエントリーポイントの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, patch


class TestMain:
    """main() のテスト"""

    def test_main_calls_orchestrator_run(self):
        """main() が OrchestratorAgent.run() を呼び出すこと"""
        mock_agent = MagicMock()
        mock_agent_class = MagicMock(return_value=mock_agent)

        with patch("agents.orchestrator_agent.OrchestratorAgent", mock_agent_class), \
             patch("session.session_manager.SessionManagerFactory.generate_session_id", return_value="test_session"), \
             patch("builtins.input", return_value="山田太郎"), \
             patch("builtins.print"):
            from main import main
            main()
            mock_agent.run.assert_called_once()

    def test_main_keyboard_interrupt_does_not_exit(self):
        """KeyboardInterrupt 発生時に sys.exit が呼ばれないこと"""
        with patch("builtins.input", side_effect=KeyboardInterrupt), \
             patch("builtins.print"):
            from main import main
            # sys.exit が呼ばれないことを確認（例外が発生しないこと）
            main()  # KeyboardInterrupt → print して正常終了

    def test_main_exception_calls_sys_exit(self):
        """Exception 発生時に sys.exit(1) が呼ばれること"""
        mock_agent = MagicMock()
        mock_agent.run.side_effect = RuntimeError("テストエラー")
        mock_agent_class = MagicMock(return_value=mock_agent)

        with patch("agents.orchestrator_agent.OrchestratorAgent", mock_agent_class), \
             patch("session.session_manager.SessionManagerFactory.generate_session_id", return_value="test_session"), \
             patch("builtins.input", return_value="山田太郎"), \
             patch("builtins.print"):
            with pytest.raises(SystemExit) as exc_info:
                from main import main
                main()
            assert exc_info.value.code == 1
