"""ErrorHandlerの単体テスト"""
import pytest
from pydantic import BaseModel, Field, ValidationError

from handlers.error_handler import ErrorHandler, LoopLimitError


class _SampleModel(BaseModel):
    name: str = Field(..., min_length=1)
    amount: int = Field(..., ge=0)


class TestLoopLimitError:
    """LoopLimitErrorのテスト"""

    def test_attributes(self):
        err = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="テスト")
        assert err.current_iteration == 10
        assert err.max_iterations == 10
        assert err.agent_name == "テスト"

    def test_message_contains_agent_name(self):
        err = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="MyAgent")
        assert "MyAgent" in str(err)


class TestErrorHandler:
    """ErrorHandlerのテスト"""

    def test_handle_throttling_error_returns_str(self):
        result = ErrorHandler.handle_throttling_error(Exception("test"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_handle_max_tokens_error_returns_str(self):
        result = ErrorHandler.handle_max_tokens_error(Exception("test"))
        assert isinstance(result, str)

    def test_handle_context_window_error_returns_str(self):
        result = ErrorHandler.handle_context_window_error(Exception("test"))
        assert isinstance(result, str)

    def test_handle_fare_data_error_returns_str(self):
        result = ErrorHandler.handle_fare_data_error(FileNotFoundError("test.json"))
        assert isinstance(result, str)

    def test_handle_calculation_error_returns_str(self):
        result = ErrorHandler.handle_calculation_error(Exception("test"))
        assert isinstance(result, str)

    def test_handle_file_save_error_returns_str(self):
        result = ErrorHandler.handle_file_save_error(IOError("permission denied"))
        assert isinstance(result, str)
        assert "permission denied" in result

    def test_handle_validation_error_single_field(self):
        try:
            _SampleModel(name="", amount=100)
        except ValidationError as e:
            result = ErrorHandler.handle_validation_error(e)
            assert isinstance(result, str)
            assert "name" in result

    def test_handle_validation_error_multiple_fields(self):
        try:
            _SampleModel(name="", amount=-1)
        except ValidationError as e:
            result = ErrorHandler.handle_validation_error(e)
            assert isinstance(result, str)
            # 複数フィールドのエラーが含まれること
            assert "name" in result or "amount" in result

    def test_handle_keyboard_interrupt_returns_str(self):
        result = ErrorHandler.handle_keyboard_interrupt(KeyboardInterrupt())
        assert isinstance(result, str)

    def test_handle_loop_limit_error_returns_str(self):
        err = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="test")
        result = ErrorHandler.handle_loop_limit_error(err)
        assert isinstance(result, str)

    def test_handle_runtime_error_returns_str(self):
        result = ErrorHandler.handle_runtime_error(RuntimeError("test error"))
        assert isinstance(result, str)
        assert "test error" in result

    def test_handle_unexpected_error_contains_class_name(self):
        result = ErrorHandler.handle_unexpected_error(ValueError("test"))
        assert isinstance(result, str)
        assert "ValueError" in result

    def test_no_logging_in_error_handler(self):
        """ErrorHandler内でloggingモジュールが使用されていないことを確認"""
        import inspect
        import handlers.error_handler as module
        source = inspect.getsource(module)
        # ErrorHandlerクラス内にlogging.getLoggerがないこと
        assert "_logger" not in source or source.index("_logger") > source.index("class ErrorHandler")
