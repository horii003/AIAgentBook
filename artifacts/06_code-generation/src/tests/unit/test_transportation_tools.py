"""交通費計算ツールの単体テスト"""
import json
import os
import pytest
from unittest.mock import MagicMock, patch

import tools.transportation_tools as tt


def _make_tool_context(application_date="2026-05-23"):
    ctx = MagicMock()
    ctx.invocation_state = {"application_date": application_date}
    return ctx


def _reset_cache():
    """テスト間でキャッシュをリセット"""
    tt._train_fares = []
    tt._train_fares_loaded = False
    tt._fixed_fares = {}
    tt._fixed_fares_loaded = False


class TestLoadTrainFares:
    """_load_train_fares関数のテスト"""

    def setup_method(self):
        _reset_cache()

    def test_file_not_found(self):
        with patch("os.path.exists", return_value=False):
            ok, err = tt._load_train_fares()
        assert ok is False
        assert isinstance(err, str)

    def test_success(self, tmp_path):
        data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        fares_file = tmp_path / "train_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_TRAIN_FARES_PATH", str(fares_file)):
            ok, err = tt._load_train_fares()
        assert ok is True
        assert err == ""

    def test_cached_on_second_call(self, tmp_path):
        data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        fares_file = tmp_path / "train_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_TRAIN_FARES_PATH", str(fares_file)):
            tt._load_train_fares()
            # 2回目はキャッシュから
            with patch("builtins.open", side_effect=Exception("should not open")):
                ok, err = tt._load_train_fares()
        assert ok is True


class TestCalculateTransportationCost:
    """calculate_transportation_cost関数のテスト"""

    def setup_method(self):
        _reset_cache()

    def _call(self, departure, destination, transport_type, travel_date, app_date="2026-05-23"):
        ctx = _make_tool_context(app_date)
        # ツール関数を直接呼び出す（@toolデコレータをバイパス）
        return tt.calculate_transportation_cost.__wrapped__(
            departure=departure,
            destination=destination,
            transport_type=transport_type,
            travel_date=travel_date,
            tool_context=ctx,
        )

    def test_train_known_route(self, tmp_path):
        data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        fares_file = tmp_path / "train_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_TRAIN_FARES_PATH", str(fares_file)):
            result = self._call("東京", "新宿", "電車", "2026-05-23")

        assert result["success"] is True
        assert result["fare"] == 200

    def test_train_unknown_route(self, tmp_path):
        data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        fares_file = tmp_path / "train_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_TRAIN_FARES_PATH", str(fares_file)):
            result = self._call("大阪", "京都", "電車", "2026-05-23")

        assert result["success"] is False
        assert "大阪" in result["error_message"]

    def test_bus_fixed_fare(self, tmp_path):
        data = {"bus": 220, "taxi": 2000, "airplane": 50000}
        fares_file = tmp_path / "fixed_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_FIXED_FARES_PATH", str(fares_file)):
            result = self._call("A", "B", "バス", "2026-05-23")

        assert result["success"] is True
        assert result["fare"] == 220

    def test_taxi_fixed_fare(self, tmp_path):
        data = {"bus": 220, "taxi": 2000, "airplane": 50000}
        fares_file = tmp_path / "fixed_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_FIXED_FARES_PATH", str(fares_file)):
            result = self._call("A", "B", "タクシー", "2026-05-23")

        assert result["success"] is True
        assert result["fare"] == 2000

    def test_airplane_fixed_fare(self, tmp_path):
        data = {"bus": 220, "taxi": 2000, "airplane": 50000}
        fares_file = tmp_path / "fixed_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_FIXED_FARES_PATH", str(fares_file)):
            result = self._call("A", "B", "飛行機", "2026-05-23")

        assert result["success"] is True
        assert result["fare"] == 50000

    def test_is_expired_false_within_deadline(self, tmp_path):
        data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        fares_file = tmp_path / "train_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_TRAIN_FARES_PATH", str(fares_file)):
            # 申請日2026-05-23、移動日2026-04-01（3ヶ月以内）
            result = self._call("東京", "新宿", "電車", "2026-04-01", "2026-05-23")

        assert result["is_expired"] is False

    def test_is_expired_true_over_deadline(self, tmp_path):
        data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        fares_file = tmp_path / "train_fares.json"
        fares_file.write_text(json.dumps(data), encoding="utf-8")

        with patch.object(tt, "_TRAIN_FARES_PATH", str(fares_file)):
            # 申請日2026-05-23、移動日2026-01-01（3ヶ月超過）
            result = self._call("東京", "新宿", "電車", "2026-01-01", "2026-05-23")

        assert result["is_expired"] is True

    def test_empty_departure_returns_error(self):
        ctx = _make_tool_context()
        result = tt.calculate_transportation_cost.__wrapped__(
            departure="",
            destination="新宿",
            transport_type="電車",
            travel_date="2026-05-23",
            tool_context=ctx,
        )
        assert result["success"] is False

    def test_invalid_transport_type_returns_error(self):
        ctx = _make_tool_context()
        result = tt.calculate_transportation_cost.__wrapped__(
            departure="東京",
            destination="新宿",
            transport_type="自転車",
            travel_date="2026-05-23",
            tool_context=ctx,
        )
        assert result["success"] is False
