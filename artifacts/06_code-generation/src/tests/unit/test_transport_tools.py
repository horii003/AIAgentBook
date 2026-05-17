"""交通費計算ツールの単体テスト"""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from tools import transport_tools
from tools.transport_tools import calculate_transport_fare

# @tool デコレータでラップされた関数の元関数を取得
_calculate_fare = calculate_transport_fare.__wrapped__


@pytest.fixture(autouse=True)
def reset_cache():
    """テストごとにキャッシュをリセット"""
    transport_tools._train_routes = []
    transport_tools._train_routes_loaded = False
    transport_tools._fixed_fares = {}
    transport_tools._fixed_fares_loaded = False
    yield


class TestCalculateTransportFare:
    """calculate_transport_fare のテスト"""

    def test_train_fare(self, tmp_path, monkeypatch):
        """電車の正しい運賃返却"""
        data = {"routes": [{"departure": "渋谷", "destination": "新宿", "fare": 170}]}
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "train_fares.json").write_text(json.dumps(data), encoding="utf-8")
        monkeypatch.setattr(transport_tools, "_DATA_DIR", data_dir)

        result = _calculate_fare(
            departure="渋谷", destination="新宿", transport_type="電車", travel_date="2026-05-17"
        )
        assert result["success"] is True
        assert result["fare"] == 170

    def test_bus_fare(self, tmp_path, monkeypatch):
        """バスの固定運賃返却"""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "fixed_fares.json").write_text(
            json.dumps({"bus": 220, "taxi": 2000, "airplane": 50000}), encoding="utf-8"
        )
        monkeypatch.setattr(transport_tools, "_DATA_DIR", data_dir)

        result = _calculate_fare(
            departure="A", destination="B", transport_type="バス", travel_date="2026-05-17"
        )
        assert result["success"] is True
        assert result["fare"] == 220

    def test_taxi_fare(self, tmp_path, monkeypatch):
        """タクシーの固定運賃返却"""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "fixed_fares.json").write_text(
            json.dumps({"bus": 220, "taxi": 2000, "airplane": 50000}), encoding="utf-8"
        )
        monkeypatch.setattr(transport_tools, "_DATA_DIR", data_dir)

        result = _calculate_fare(
            departure="A", destination="B", transport_type="タクシー", travel_date="2026-05-17"
        )
        assert result["success"] is True
        assert result["fare"] == 2000

    def test_route_not_found(self, tmp_path, monkeypatch):
        """経路不存在時のエラー返却"""
        data = {"routes": [{"departure": "渋谷", "destination": "新宿", "fare": 170}]}
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "train_fares.json").write_text(json.dumps(data), encoding="utf-8")
        monkeypatch.setattr(transport_tools, "_DATA_DIR", data_dir)

        result = _calculate_fare(
            departure="品川", destination="横浜", transport_type="電車", travel_date="2026-05-17"
        )
        assert result["success"] is False
        assert "見つかりません" in result["error_message"]

    def test_file_not_found(self, tmp_path, monkeypatch):
        """JSONファイル不存在時のエラー返却"""
        data_dir = tmp_path / "empty"
        data_dir.mkdir()
        monkeypatch.setattr(transport_tools, "_DATA_DIR", data_dir)

        result = _calculate_fare(
            departure="渋谷", destination="新宿", transport_type="電車", travel_date="2026-05-17"
        )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_validation_error_empty_departure(self):
        """空文字入力時のバリデーションエラー"""
        result = _calculate_fare(
            departure="", destination="新宿", transport_type="電車", travel_date="2026-05-17"
        )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_station_name_normalization(self, tmp_path, monkeypatch):
        """駅名末尾「駅」除去の正規化動作"""
        data = {"routes": [{"departure": "渋谷", "destination": "新宿", "fare": 170}]}
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "train_fares.json").write_text(json.dumps(data), encoding="utf-8")
        monkeypatch.setattr(transport_tools, "_DATA_DIR", data_dir)

        result = _calculate_fare(
            departure="渋谷駅", destination="新宿駅", transport_type="train", travel_date="2026-05-17"
        )
        assert result["success"] is True
        assert result["fare"] == 170
