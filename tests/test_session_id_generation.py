"""セッションID生成機能のテスト"""
import pytest
from session.session_manager import SessionManagerFactory


class TestSessionIDGeneration:
    """セッションID生成機能のテスト"""
    
    def test_generate_session_id_without_prefix(self):
        """プレフィックスなしのセッションID生成テスト"""
        session_id = SessionManagerFactory.generate_session_id()
        
        assert session_id is not None
        assert isinstance(session_id, str)
        
        # フォーマット確認: YYYYMMDD_HHMMSS_uuid8
        parts = session_id.split("_")
        assert len(parts) == 3, f"Expected 3 parts, got {len(parts)}: {session_id}"
        
        # 日付部分（YYYYMMDD）
        assert len(parts[0]) == 8, f"Date part should be 8 chars: {parts[0]}"
        assert parts[0].isdigit(), f"Date part should be numeric: {parts[0]}"
        
        # 時刻部分（HHMMSS）
        assert len(parts[1]) == 6, f"Time part should be 6 chars: {parts[1]}"
        assert parts[1].isdigit(), f"Time part should be numeric: {parts[1]}"
        
        # UUID部分（8文字）
        assert len(parts[2]) == 8, f"UUID part should be 8 chars: {parts[2]}"
        
        print(f"\n✅ セッションID生成成功（プレフィックスなし）: {session_id}")
    
    def test_generate_session_id_with_prefix(self):
        """プレフィックスありのセッションID生成テスト"""
        prefix = "test"
        session_id = SessionManagerFactory.generate_session_id(prefix=prefix)
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert session_id.startswith(f"{prefix}_"), f"Should start with '{prefix}_': {session_id}"
        
        # フォーマット確認: prefix_YYYYMMDD_HHMMSS_uuid8
        parts = session_id.split("_")
        assert len(parts) == 4, f"Expected 4 parts with prefix, got {len(parts)}: {session_id}"
        assert parts[0] == prefix, f"First part should be prefix '{prefix}': {parts[0]}"
        
        print(f"\n✅ セッションID生成成功（プレフィックスあり）: {session_id}")
    
    def test_generate_session_id_uniqueness(self):
        """セッションIDの一意性テスト"""
        # 複数のセッションIDを生成して重複がないことを確認
        session_ids = set()
        for _ in range(100):
            session_id = SessionManagerFactory.generate_session_id()
            session_ids.add(session_id)
        
        # すべてのIDが一意であることを確認
        assert len(session_ids) == 100, "All session IDs should be unique"
        
        print(f"\n✅ セッションID一意性テスト成功: 100個のIDがすべて一意")
    
    def test_generate_session_id_with_various_prefixes(self):
        """様々なプレフィックスでのセッションID生成テスト"""
        prefixes = ["user", "admin", "test_user_a", "session123"]
        
        for prefix in prefixes:
            session_id = SessionManagerFactory.generate_session_id(prefix=prefix)
            assert session_id.startswith(f"{prefix}_"), f"Should start with '{prefix}_': {session_id}"
            print(f"  - {prefix}: {session_id}")
        
        print(f"\n✅ 様々なプレフィックスでのセッションID生成成功")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
