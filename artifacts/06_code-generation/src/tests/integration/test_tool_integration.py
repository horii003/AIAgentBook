"""ツール連携の結合テスト"""

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from tools import transport_tools
from tools.transport_tools import calculate_transport_fare

_calculate_fare = calculate_transport_fare.__wrapped__


@pytest.fixture(autouse=True)
def reset_cache():
    """テストごとにキャッシュをリセット"""
    transport_tools._train_routes = []
    transport_tools._train_routes_loaded = False
    transport_tools._fixed_fares = {}
    transport_tools._fixed_fares_loaded = False
    yield


class TestTransportCalculationFlow:
    """交通費計算→申請書生成の一連フロー"""

    def test_calculate_multiple_routes(self, tmp_path, monkeypatch):
        """複数区間の交通費計算が正しく動作すること"""
        data = {
            "routes": [
                {"departure": "渋谷", "destination": "新宿", "fare": 170},
                {"departure": "新宿", "destination": "東京", "fare": 200},
            ]
        }
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        (data_dir / "train_fares.json").write_text(json.dumps(data), encoding="utf-8")
        (data_dir / "fixed_fares.json").write_text(
            json.dumps({"bus": 220, "taxi": 2000, "airplane": 50000}), encoding="utf-8"
        )
        monkeypatch.setattr(transport_tools, "_DATA_DIR", data_dir)

        # 電車区間1
        r1 = _calculate_fare(
            departure="渋谷", destination="新宿", transport_type="電車", travel_date="2026-05-17"
        )
        assert r1["success"] is True
        assert r1["fare"] == 170

        # 電車区間2
        r2 = _calculate_fare(
            departure="新宿", destination="東京", transport_type="電車", travel_date="2026-05-17"
        )
        assert r2["success"] is True
        assert r2["fare"] == 200

        # バス区間
        r3 = _calculate_fare(
            departure="A", destination="B", transport_type="バス", travel_date="2026-05-17"
        )
        assert r3["success"] is True
        assert r3["fare"] == 220

        # 合計
        total = r1["fare"] + r2["fare"] + r3["fare"]
        assert total == 590

    def test_error_propagation(self, tmp_path, monkeypatch):
        """エラーが正しく伝播すること"""
        data_dir = tmp_path / "empty"
        data_dir.mkdir()
        monkeypatch.setattr(transport_tools, "_DATA_DIR", data_dir)

        result = _calculate_fare(
            departure="渋谷", destination="新宿", transport_type="電車", travel_date="2026-05-17"
        )
        assert result["success"] is False
        assert result["error_message"] is not None
        assert isinstance(result["error_message"], str)
