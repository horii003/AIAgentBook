"""main.pyの単体テスト"""
import pytest
from unittest.mock import MagicMock, patch


class TestMain:
    def test_main_calls_orchestrator_run(self):
        """main()がOrchestratorAgent.run()を呼び出すこと"""
        mock_agent = MagicMock()
        with patch("main.OrchestratorAgent", return_value=mock_agent):
            with patch("main.SessionManagerFactory.generate_session_id", return_value="test_session"):
                from main import main
                main()
        mock_agent.run.assert_called_once()

    def test_main_keyboard_interrupt_no_exit(self):
        """KeyboardInterrupt発生時にsys.exitが呼ばれないこと"""
        mock_agent = MagicMock()
        mock_agent.run.side_effect = KeyboardInterrupt()
        with patch("main.OrchestratorAgent", return_value=mock_agent):
            with patch("main.SessionManagerFactory.generate_session_id", return_value="test_session"):
                with patch("builtins.print"):
                    from main import main
                    main()  # sys.exitが呼ばれないこと（例外が発生しないこと）

    def test_main_exception_calls_sys_exit(self):
        """Exception発生時にsys.exit(1)が呼ばれること"""
        import sys
        mock_agent = MagicMock()
        mock_agent.run.side_effect = Exception("テストエラー")
        with patch("main.OrchestratorAgent", return_value=mock_agent):
            with patch("main.SessionManagerFactory.generate_session_id", return_value="test_session"):
                with patch("builtins.print"):
                    with pytest.raises(SystemExit) as exc_info:
                        from main import main
                        main()
        assert exc_info.value.code == 1
