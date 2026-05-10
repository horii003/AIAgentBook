"""ErrorHandlerの単体テスト"""
import pytest
from pydantic import ValidationError
from handlers.error_handler import ErrorHandler, LoopLimitError
from models.data_models import TransportCalculatorInput


class TestErrorHandler:
    def test_handle_validation_error_returns_message(self):
        """TC-UNIT-040: ValidationErrorで日本語メッセージが返ること"""
        try:
            TransportCalculatorInput(
                departure="東京", destination="大阪",
                transport_type="自転車", travel_date="2026-05-10"
            )
        except ValidationError as e:
            msg = ErrorHandler.handle_validation_error(e)
            assert isinstance(msg, str)
            assert len(msg) > 0

    def test_handle_loop_limit_error_returns_message(self):
        """TC-UNIT-041: LoopLimitErrorで日本語メッセージが返ること"""
        error = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="テスト")
        msg = ErrorHandler.handle_loop_limit_error(error)
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_unexpected_error_returns_message(self):
        """TC-UNIT-042: 予期しない例外で日本語メッセージが返ること"""
        error = Exception("テストエラー")
        msg = ErrorHandler.handle_unexpected_error(error)
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_keyboard_interrupt(self):
        msg = ErrorHandler.handle_keyboard_interrupt()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_throttling_error(self):
        msg = ErrorHandler.handle_throttling_error()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_max_tokens_error(self):
        msg = ErrorHandler.handle_max_tokens_error()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_context_window_error(self):
        msg = ErrorHandler.handle_context_window_error()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_fare_data_error(self):
        msg = ErrorHandler.handle_fare_data_error()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_calculation_error(self):
        msg = ErrorHandler.handle_calculation_error()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_file_save_error(self):
        msg = ErrorHandler.handle_file_save_error()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_handle_runtime_error(self):
        msg = ErrorHandler.handle_runtime_error()
        assert isinstance(msg, str)
        assert len(msg) > 0

    def test_static_call_without_instance(self):
        """ErrorHandlerをインスタンス化せずに静的呼び出しできること"""
        msg = ErrorHandler.handle_unexpected_error(Exception("test"))
        assert isinstance(msg, str)


class TestLoopLimitError:
    def test_attributes(self):
        error = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="テスト")
        assert error.current_iteration == 5
        assert error.max_iterations == 10
        assert error.agent_name == "テスト"

    def test_message_contains_info(self):
        error = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="テスト")
        assert "10" in str(error)
        assert "テスト" in str(error)
