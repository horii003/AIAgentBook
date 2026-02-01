"""InvocationStateの統合テスト"""
import pytest
from unittest.mock import Mock, patch
from pydantic import ValidationError
from models.data_models import InvocationState
from tools.excel_generator import _get_applicant_name, _get_application_date


class TestInvocationStateIntegration:
    """InvocationStateの実際の使用シナリオテスト"""
    
    def test_get_applicant_name_with_valid_state(self):
        """正常なinvocation_stateから申請者名を取得"""
        mock_context = Mock()
        mock_context.invocation_state = {
            "applicant_name": "田中太郎",
            "application_date": "2025-01-15",
            "session_id": "abc123"
        }
        
        result = _get_applicant_name(mock_context)
        assert result == "田中太郎"
        print("✅ 正常なinvocation_stateから申請者名を取得")
    
    def test_get_applicant_name_with_invalid_state(self):
        """不正なinvocation_stateの場合はデフォルト値を返す"""
        mock_context = Mock()
        mock_context.invocation_state = {
            "applicant_name": 12345,  # 数値（不正）
            "application_date": "2025-01-15"
        }
        
        result = _get_applicant_name(mock_context)
        assert result == "未設定"
        print("✅ 不正なinvocation_stateの場合はデフォルト値を返す")
    
    def test_get_applicant_name_with_empty_context(self):
        """invocation_stateがない場合はデフォルト値を返す"""
        mock_context = Mock()
        mock_context.invocation_state = None
        
        result = _get_applicant_name(mock_context)
        assert result == "未設定"
        print("✅ invocation_stateがない場合はデフォルト値を返す")
    
    def test_get_application_date_with_valid_state(self):
        """正常なinvocation_stateから申請日を取得"""
        mock_context = Mock()
        mock_context.invocation_state = {
            "applicant_name": "田中太郎",
            "application_date": "2025-01-15",
            "session_id": "abc123"
        }
        
        result = _get_application_date(mock_context)
        assert result == "2025-01-15"
        print("✅ 正常なinvocation_stateから申請日を取得")
    
    def test_get_application_date_with_invalid_date_format(self):
        """不正な日付形式の場合は現在日付を返す"""
        mock_context = Mock()
        mock_context.invocation_state = {
            "applicant_name": "田中太郎",
            "application_date": "2025/01/15"  # スラッシュ区切り（不正）
        }
        
        result = _get_application_date(mock_context)
        # 現在日付が返される（YYYY-MM-DD形式）
        assert len(result) == 10
        assert result[4] == "-"
        assert result[7] == "-"
        print("✅ 不正な日付形式の場合は現在日付を返す")
    
    def test_get_application_date_with_empty_context(self):
        """invocation_stateがない場合は現在日付を返す"""
        mock_context = Mock()
        mock_context.invocation_state = None
        
        result = _get_application_date(mock_context)
        # 現在日付が返される（YYYY-MM-DD形式）
        assert len(result) == 10
        assert result[4] == "-"
        assert result[7] == "-"
        print("✅ invocation_stateがない場合は現在日付を返す")
    
    def test_invocation_state_validation_in_agent_context(self):
        """エージェントコンテキストでのバリデーション"""
        # 正常なケース
        valid_state = {
            "applicant_name": "田中太郎",
            "application_date": "2025-01-15",
            "session_id": "abc123"
        }
        
        state = InvocationState(**valid_state)
        assert state.applicant_name == "田中太郎"
        assert state.application_date == "2025-01-15"
        assert state.session_id == "abc123"
        print("✅ エージェントコンテキストでのバリデーションが正常に機能")
    
    def test_invocation_state_error_handling(self):
        """エラーハンドリングのテスト"""
        invalid_state = {
            "applicant_name": "",  # 空文字列
            "application_date": "2025-01-15"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InvocationState(**invalid_state)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "applicant_name" in str(errors[0]["loc"])
        print("✅ エラーハンドリングが正常に機能")
    
    def test_invocation_state_with_extra_fields(self):
        """余分なフィールドがある場合の動作確認"""
        state_with_extra = {
            "applicant_name": "田中太郎",
            "application_date": "2025-01-15",
            "session_id": "abc123",
            "extra_field": "これは無視される"  # 余分なフィールド
        }
        
        # Pydanticはデフォルトで余分なフィールドを無視する
        state = InvocationState(**state_with_extra)
        assert state.applicant_name == "田中太郎"
        assert not hasattr(state, "extra_field")
        print("✅ 余分なフィールドは無視される")
    
    def test_invocation_state_type_coercion(self):
        """型変換のテスト"""
        # session_idがNoneの場合
        state = InvocationState(
            applicant_name="田中太郎",
            application_date="2025-01-15",
            session_id=None
        )
        assert state.session_id is None
        print("✅ session_idがNoneの場合も正常に処理")


class TestInvocationStateErrorMessages:
    """InvocationStateのエラーメッセージテスト"""
    
    def test_detailed_error_message_for_empty_name(self):
        """空の申請者名の詳細なエラーメッセージ"""
        try:
            InvocationState(
                applicant_name="",
                application_date="2025-01-15"
            )
            assert False, "ValidationErrorが発生するはず"
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{field}: {error['msg']}")
            
            assert len(error_messages) > 0
            assert "applicant_name" in error_messages[0]
            print(f"✅ 詳細なエラーメッセージ: {error_messages}")
    
    def test_detailed_error_message_for_invalid_date(self):
        """無効な日付の詳細なエラーメッセージ"""
        try:
            InvocationState(
                applicant_name="田中太郎",
                application_date="2025/01/15"
            )
            assert False, "ValidationErrorが発生するはず"
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{field}: {error['msg']}")
            
            assert len(error_messages) > 0
            assert "application_date" in error_messages[0]
            assert "YYYY-MM-DD" in error_messages[0]
            print(f"✅ 詳細なエラーメッセージ: {error_messages}")
    
    def test_multiple_errors_message(self):
        """複数のエラーの詳細なメッセージ"""
        try:
            InvocationState(
                applicant_name="",
                application_date="invalid-date"
            )
            assert False, "ValidationErrorが発生するはず"
        except ValidationError as e:
            error_messages = []
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                error_messages.append(f"{field}: {error['msg']}")
            
            assert len(error_messages) >= 2
            print(f"✅ 複数のエラーメッセージ: {error_messages}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
