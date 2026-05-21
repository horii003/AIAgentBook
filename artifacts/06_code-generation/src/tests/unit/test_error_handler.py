"""エラーハンドラーの単体テスト"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from pydantic import BaseModel, Field, ValidationError
from handlers.error_handler import LoopLimitError, ErrorHandler


class TestLoopLimitError:
    """LoopLimitError のテスト"""

    def test_init_fields(self):
        """フィールド値が正しく設定されること"""
        err = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="テストエージェント")
        assert err.current_iteration == 5
        assert err.max_iterations == 10
        assert err.agent_name == "テストエージェント"

    def test_message_contains_agent_name(self):
        """メッセージにエージェント名が含まれること"""
        err = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="テストエージェント")
        assert "テストエージェント" in str(err)

    def test_message_contains_max_iterations(self):
        """メッセージにループ回数が含まれること"""
        err = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="テストエージェント")
        assert "10" in str(err)

    def test_is_runtime_error(self):
        """RuntimeError のサブクラスであること"""
        err = LoopLimitError(current_iteration=1, max_iterations=5, agent_name="Agent")
        assert isinstance(err, RuntimeError)


class TestErrorHandler:
    """ErrorHandler のテスト"""

    def test_handle_throttling_error_returns_str(self):
        """handle_throttling_error が文字列を返すこと"""
        result = ErrorHandler.handle_throttling_error(Exception("throttle"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_handle_max_tokens_error_returns_str(self):
        """handle_max_tokens_error が文字列を返すこと"""
        result = ErrorHandler.handle_max_tokens_error(Exception("max tokens"))
        assert isinstance(result, str)

    def test_handle_context_window_error_returns_str(self):
        """handle_context_window_error が文字列を返すこと"""
        result = ErrorHandler.handle_context_window_error(Exception("context"))
        assert isinstance(result, str)

    def test_handle_fare_data_error_returns_str(self):
        """handle_fare_data_error が文字列を返すこと"""
        result = ErrorHandler.handle_fare_data_error(FileNotFoundError("file"))
        assert isinstance(result, str)

    def test_handle_calculation_error_returns_str(self):
        """handle_calculation_error が文字列を返すこと"""
        result = ErrorHandler.handle_calculation_error(ValueError("calc"))
        assert isinstance(result, str)

    def test_handle_file_save_error_returns_str(self):
        """handle_file_save_error が文字列を返すこと"""
        result = ErrorHandler.handle_file_save_error(IOError("save"))
        assert isinstance(result, str)

    def test_handle_keyboard_interrupt_returns_str(self):
        """handle_keyboard_interrupt が文字列を返すこと"""
        result = ErrorHandler.handle_keyboard_interrupt()
        assert isinstance(result, str)

    def test_handle_keyboard_interrupt_with_none(self):
        """引数 None を渡してもエラーにならないこと"""
        result = ErrorHandler.handle_keyboard_interrupt(None)
        assert isinstance(result, str)

    def test_handle_runtime_error_returns_str(self):
        """handle_runtime_error が文字列を返すこと"""
        result = ErrorHandler.handle_runtime_error(RuntimeError("runtime"))
        assert isinstance(result, str)

    def test_handle_runtime_error_with_none(self):
        """引数 None を渡してもエラーにならないこと"""
        result = ErrorHandler.handle_runtime_error(None)
        assert isinstance(result, str)

    def test_handle_unexpected_error_returns_str(self):
        """handle_unexpected_error が文字列を返すこと"""
        result = ErrorHandler.handle_unexpected_error(Exception("unexpected"))
        assert isinstance(result, str)

    def test_handle_unexpected_error_with_none(self):
        """引数 None を渡してもエラーにならないこと"""
        result = ErrorHandler.handle_unexpected_error(None)
        assert isinstance(result, str)

    def test_handle_validation_error_contains_field_info(self):
        """handle_validation_error が ValidationError のフィールド情報を含むメッセージを返すこと"""
        class _TestModel(BaseModel):
            amount: int = Field(..., ge=0)

        try:
            _TestModel(amount=-1)
        except ValidationError as e:
            result = ErrorHandler.handle_validation_error(e)
            assert isinstance(result, str)
            assert "amount" in result

    def test_handle_loop_limit_error_contains_agent_name_and_iterations(self):
        """handle_loop_limit_error がエージェント名・ループ回数を含むメッセージを返すこと"""
        err = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="交通費エージェント")
        result = ErrorHandler.handle_loop_limit_error(err)
        assert isinstance(result, str)
        assert "交通費エージェント" in result
        assert "10" in result
