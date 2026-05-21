"""ErrorHandler の単体テスト"""
import pytest
from pydantic import BaseModel, Field, ValidationError

from handlers.error_handler import ErrorHandler, LoopLimitError


class TestLoopLimitError:
    """LoopLimitError のテスト"""

    def test_attributes(self):
        """属性値が正しく設定されること"""
        err = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="テストエージェント")
        assert err.current_iteration == 10
        assert err.max_iterations == 10
        assert err.agent_name == "テストエージェント"

    def test_message_contains_agent_name(self):
        """メッセージにエージェント名が含まれること"""
        err = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="交通費エージェント")
        assert "交通費エージェント" in str(err)

    def test_message_contains_max_iterations(self):
        """メッセージに最大ループ回数が含まれること"""
        err = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="テスト")
        assert "10" in str(err)

    def test_is_runtime_error(self):
        """RuntimeError のサブクラスであること"""
        err = LoopLimitError(current_iteration=5, max_iterations=10, agent_name="テスト")
        assert isinstance(err, RuntimeError)


class TestErrorHandlerStaticMethods:
    """ErrorHandler が staticmethod であることのテスト"""

    def test_no_instantiation_needed(self):
        """インスタンス化不要でクラスメソッドとして呼び出せること"""
        result = ErrorHandler.handle_keyboard_interrupt()
        assert isinstance(result, str)


class TestHandleKeyboardInterrupt:
    """handle_keyboard_interrupt のテスト"""

    def test_returns_string(self):
        """文字列を返すこと"""
        result = ErrorHandler.handle_keyboard_interrupt()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_japanese_message(self):
        """日本語メッセージを返すこと"""
        result = ErrorHandler.handle_keyboard_interrupt()
        assert "中断" in result


class TestHandleLoopLimitError:
    """handle_loop_limit_error のテスト"""

    def test_returns_string(self):
        """文字列を返すこと"""
        err = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="テスト")
        result = ErrorHandler.handle_loop_limit_error(err)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_japanese_message(self):
        """日本語メッセージを返すこと"""
        err = LoopLimitError(current_iteration=10, max_iterations=10, agent_name="テスト")
        result = ErrorHandler.handle_loop_limit_error(err)
        assert "上限" in result or "処理" in result


class TestHandleValidationError:
    """handle_validation_error のテスト"""

    def _create_validation_error(self):
        """テスト用のValidationErrorを生成する"""
        class TestModel(BaseModel):
            name: str = Field(..., min_length=1)

        try:
            TestModel(name="")
        except ValidationError as e:
            return e
        return None

    def test_returns_string(self):
        """文字列を返すこと"""
        err = self._create_validation_error()
        result = ErrorHandler.handle_validation_error(err)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_japanese_message(self):
        """日本語メッセージを返すこと"""
        err = self._create_validation_error()
        result = ErrorHandler.handle_validation_error(err)
        assert "入力内容" in result or "誤り" in result


class TestHandleRuntimeError:
    """handle_runtime_error のテスト"""

    def test_returns_string(self):
        """文字列を返すこと"""
        result = ErrorHandler.handle_runtime_error(RuntimeError("テストエラー"))
        assert isinstance(result, str)
        assert len(result) > 0


class TestHandleUnexpectedError:
    """handle_unexpected_error のテスト"""

    def test_returns_string(self):
        """文字列を返すこと"""
        result = ErrorHandler.handle_unexpected_error(Exception("テストエラー"))
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_japanese_message(self):
        """日本語メッセージを返すこと"""
        result = ErrorHandler.handle_unexpected_error()
        assert "エラー" in result


class TestHandleFareDataError:
    """handle_fare_data_error のテスト"""

    def test_file_not_found_error(self):
        """FileNotFoundError の場合に適切なメッセージを返すこと"""
        result = ErrorHandler.handle_fare_data_error(FileNotFoundError("ファイルなし"))
        assert isinstance(result, str)
        assert "見つかりません" in result

    def test_general_exception(self):
        """一般的な例外の場合に適切なメッセージを返すこと"""
        result = ErrorHandler.handle_fare_data_error(Exception("読み込みエラー"))
        assert isinstance(result, str)
        assert "失敗" in result


class TestHandleFileSaveError:
    """handle_file_save_error のテスト"""

    def test_io_error(self):
        """IOError の場合に適切なメッセージを返すこと"""
        result = ErrorHandler.handle_file_save_error(IOError("書き込みエラー"))
        assert isinstance(result, str)
        assert "保存" in result

    def test_permission_error(self):
        """PermissionError の場合に権限エラーメッセージを返すこと"""
        result = ErrorHandler.handle_file_save_error(PermissionError("権限なし"))
        assert isinstance(result, str)
        assert "権限" in result

    def test_general_exception(self):
        """一般的な例外の場合に適切なメッセージを返すこと"""
        result = ErrorHandler.handle_file_save_error(Exception("予期しないエラー"))
        assert isinstance(result, str)
        assert "エラー" in result
