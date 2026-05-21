"""交通費計算ツールの単体テスト"""
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
from unittest.mock import MagicMock, patch
import tools.transport_tools as tt


def _make_tool_context(applicant_name="山田太郎", application_date="2026-01-15"):
    ctx = MagicMock()
    ctx.invocation_state = {"applicant_name": applicant_name, "application_date": application_date}
    return ctx


class TestLoadTrainRoutes:
    """_load_train_routes のテスト"""

    def setup_method(self):
        """各テスト前にキャッシュをリセットする。"""
        tt._train_routes = []
        tt._train_routes_loaded = False

    def test_success_with_valid_json(self, tmp_path):
        """正常系: JSONファイル読み込み成功"""
        data = {"routes": [{"departure": "渋谷", "destination": "新宿", "fare": 200}]}
        json_file = tmp_path / "train_routes.json"
        json_file.write_text(json.dumps(data), encoding="utf-8")

        original = tt._TRAIN_ROUTES_PATH
        tt._TRAIN_ROUTES_PATH = str(json_file)
        try:
            ok, msg = tt._load_train_routes()
            assert ok is True
            assert tt._train_routes_loaded is True
            assert len(tt._train_routes) == 1
        finally:
            tt._TRAIN_ROUTES_PATH = original
            tt._train_routes = []
            tt._train_routes_loaded = False

    def test_failure_file_not_found(self):
        """異常系: ファイル不存在時に (False, エラーメッセージ) を返すこと"""
        original = tt._TRAIN_ROUTES_PATH
        tt._TRAIN_ROUTES_PATH = "/nonexistent/path/train_routes.json"
        try:
            ok, msg = tt._load_train_routes()
            assert ok is False
            assert isinstance(msg, str)
            assert len(msg) > 0
        finally:
            tt._TRAIN_ROUTES_PATH = original


class TestCalculateTransportFare:
    """calculate_transport_fare のテスト"""

    def setup_method(self):
        """各テスト前にキャッシュをリセットする。"""
        tt._train_routes = [
            {"departure": "渋谷", "destination": "新宿", "fare": 200},
            {"departure": "新宿", "destination": "渋谷", "fare": 200},
        ]
        tt._train_routes_loaded = True
        tt._fixed_fares = {"bus": 220, "taxi": 2000, "airplane": 50000}
        tt._fixed_fares_loaded = True

    def test_train_existing_route(self):
        """電車正常系: 既存経路の運賃を返すこと"""
        ctx = _make_tool_context()
        result = tt.calculate_transport_fare.__wrapped__(
            departure="渋谷",
            destination="新宿",
            transport_type="電車",
            travel_date="2026-01-15",
            tool_context=ctx,
        )
        assert result["success"] is True
        assert result["fare"] == 200

    def test_train_nonexistent_route(self):
        """電車異常系: 存在しない経路で success=False"""
        ctx = _make_tool_context()
        result = tt.calculate_transport_fare.__wrapped__(
            departure="渋谷",
            destination="横浜",
            transport_type="電車",
            travel_date="2026-01-15",
            tool_context=ctx,
        )
        assert result["success"] is False
        assert result["fare"] is None

    def test_bus_fixed_fare(self):
        """バス正常系: 固定運賃を返すこと"""
        ctx = _make_tool_context()
        result = tt.calculate_transport_fare.__wrapped__(
            departure="渋谷",
            destination="新宿",
            transport_type="バス",
            travel_date="2026-01-15",
            tool_context=ctx,
        )
        assert result["success"] is True
        assert result["fare"] == 220

    def test_taxi_fixed_fare(self):
        """タクシー正常系: 固定運賃を返すこと"""
        ctx = _make_tool_context()
        result = tt.calculate_transport_fare.__wrapped__(
            departure="渋谷",
            destination="新宿",
            transport_type="タクシー",
            travel_date="2026-01-15",
            tool_context=ctx,
        )
        assert result["success"] is True
        assert result["fare"] == 2000

    def test_airplane_fixed_fare(self):
        """飛行機正常系: 固定運賃を返すこと"""
        ctx = _make_tool_context()
        result = tt.calculate_transport_fare.__wrapped__(
            departure="東京",
            destination="大阪",
            transport_type="飛行機",
            travel_date="2026-01-15",
            tool_context=ctx,
        )
        assert result["success"] is True
        assert result["fare"] == 50000

    def test_invalid_transport_type(self):
        """不正な交通手段でバリデーションエラー"""
        ctx = _make_tool_context()
        result = tt.calculate_transport_fare.__wrapped__(
            departure="渋谷",
            destination="新宿",
            transport_type="自転車",
            travel_date="2026-01-15",
            tool_context=ctx,
        )
        assert result["success"] is False
