"""エラーハンドラーの単体テスト"""

import pytest
from pydantic import BaseModel, Field, ValidationError

from handlers.error_handler import ErrorHandler, LoopLimitError


class TestLoopLimitError:
    """LoopLimitError のテスト"""

    def test_attributes(self):
        e = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="test")
        assert e.current_iteration == 10
        assert e.max_iterations == 10
        assert e.agent_name == "test"

    def test_message(self):
        e = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="agent")
        assert "agent" in str(e)


class TestErrorHandler:
    """ErrorHandler のテスト"""

    def test_handle_throttling_error(self):
        msg = ErrorHandler.handle_throttling_error(Exception("throttled"))
        assert "利用制限" in msg

    def test_handle_max_tokens_error(self):
        msg = ErrorHandler.handle_max_tokens_error(Exception("max tokens"))
        assert "長すぎる" in msg

    def test_handle_context_window_error(self):
        msg = ErrorHandler.handle_context_window_error(Exception("overflow"))
        assert "長くなりすぎた" in msg

    def test_handle_fare_data_error(self):
        msg = ErrorHandler.handle_fare_data_error(FileNotFoundError("not found"))
        assert "運賃データ" in msg

    def test_handle_calculation_error(self):
        msg = ErrorHandler.handle_calculation_error(Exception("calc error"))
        assert "計算" in msg

    def test_handle_file_save_error(self):
        msg = ErrorHandler.handle_file_save_error(IOError("io error"))
        assert "保存" in msg

    def test_handle_validation_error(self):
        class TestModel(BaseModel):
            name: str = Field(..., min_length=1)

        try:
            TestModel(name="")
        except ValidationError as e:
            msg = ErrorHandler.handle_validation_error(e)
            assert "エラー" in msg

    def test_handle_validation_error_none_safe(self):
        # None を渡しても例外が発生しないこと
        msg = ErrorHandler.handle_validation_error(None)
        assert "エラー" in msg

    def test_handle_keyboard_interrupt(self):
        msg = ErrorHandler.handle_keyboard_interrupt(KeyboardInterrupt())
        assert "中断" in msg

    def test_handle_loop_limit_error(self):
        e = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="test")
        msg = ErrorHandler.handle_loop_limit_error(e)
        assert "上限回数" in msg

    def test_handle_runtime_error(self):
        msg = ErrorHandler.handle_runtime_error(RuntimeError("runtime"))
        assert "エラー" in msg

    def test_handle_unexpected_error(self):
        msg = ErrorHandler.handle_unexpected_error(Exception("unexpected"))
        assert "予期しない" in msg

    def test_handle_unexpected_error_none(self):
        msg = ErrorHandler.handle_unexpected_error(None)
        assert "予期しない" in msg

    def test_all_methods_return_str(self):
        """全メソッドが str を返すこと"""
        e = Exception("test")
        assert isinstance(ErrorHandler.handle_throttling_error(e), str)
        assert isinstance(ErrorHandler.handle_max_tokens_error(e), str)
        assert isinstance(ErrorHandler.handle_context_window_error(e), str)
        assert isinstance(ErrorHandler.handle_fare_data_error(e), str)
        assert isinstance(ErrorHandler.handle_calculation_error(e), str)
        assert isinstance(ErrorHandler.handle_file_save_error(e), str)
        assert isinstance(ErrorHandler.handle_keyboard_interrupt(e), str)
        assert isinstance(ErrorHandler.handle_loop_limit_error(e), str)
        assert isinstance(ErrorHandler.handle_runtime_error(e), str)
        assert isinstance(ErrorHandler.handle_unexpected_error(e), str)
