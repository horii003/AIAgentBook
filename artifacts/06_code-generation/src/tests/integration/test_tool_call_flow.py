"""ツール呼び出しフローテスト（TC-INT-010〜013）"""
import pytest
from unittest.mock import MagicMock, patch
from handlers.human_approval_hook import HumanApprovalHook


class TestToolCallFlow:
    def test_human_approval_hook_fires_before_generate_transport_form(self):
        """TC-INT-011: HumanApprovalHookがgenerate_transport_form呼び出し前に発火すること"""
        called = []
        hook = HumanApprovalHook(
            target_tools=["generate_transport_form"],
            approval_callback=lambda t, p: called.append(t) or (True, ""),
        )
        event = MagicMock()
        event.tool_use = {"name": "generate_transport_form", "input": {}}
        event.cancel_tool = False
        hook._handle_before_tool_call(event)
        assert "generate_transport_form" in called

    def test_approved_allows_tool_execution(self):
        """TC-INT-012: ユーザーOK選択後にgenerate_transport_formが呼び出されること"""
        hook = HumanApprovalHook(
            target_tools=["generate_transport_form"],
            approval_callback=lambda t, p: (True, ""),
        )
        event = MagicMock()
        event.tool_use = {"name": "generate_transport_form", "input": {}}
        event.cancel_tool = False
        hook._handle_before_tool_call(event)
        assert event.cancel_tool is False  # キャンセルされていない

    def test_cancel_prevents_tool_execution(self):
        """TC-INT-013: ユーザーキャンセル時にgenerate_transport_formが呼び出されないこと"""
        hook = HumanApprovalHook(
            target_tools=["generate_transport_form"],
            approval_callback=lambda t, p: (False, "CANCEL"),
        )
        event = MagicMock()
        event.tool_use = {"name": "generate_transport_form", "input": {}}
        event.cancel_tool = False
        hook._handle_before_tool_call(event)
        assert event.cancel_tool != False  # キャンセルメッセージが設定されている

    def test_calculate_transport_fare_returns_fare(self, tmp_data_dir):
        """TC-INT-010: calculate_transport_fareが正しい運賃を返すこと"""
        import tools.transport_tools as tt
        result = tt.calculate_transport_fare.__wrapped__("東京", "大阪", "電車", "2026-05-10")
        assert result["success"] is True
        assert result["fare"] == 13240.0
