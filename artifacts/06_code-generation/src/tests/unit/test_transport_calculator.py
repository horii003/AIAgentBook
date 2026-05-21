"""transport_calculator の単体テスト"""
import json
import sys
from unittest.mock import MagicMock, mock_open, patch

import pytest

# strands モジュールをモックとして登録
if "strands" not in sys.modules:
    mock_strands = MagicMock()
    sys.modules["strands"] = mock_strands
    sys.modules["strands.models"] = mock_strands.models

# @tool デコレータをモック（関数をそのまま返す）
import strands
strands.tool = lambda f: f

# モジュールをリロード
if "tools.transport_calculator" in sys.modules:
    del sys.modules["tools.transport_calculator"]

import tools.transport_calculator as tc


def _reset_cache():
    """キャッシュをリセットする"""
    tc._train_routes = []
    tc._train_routes_loaded = False
    tc._fixed_fares = {}
    tc._fixed_fares_loaded = False


class TestTransportCalculatorInput:
    """TransportCalculatorInput のテスト"""

    def test_valid_input(self):
        """有効な入力でインスタンスが生成されること"""
        from tools.transport_calculator import TransportCalculatorInput
        inp = TransportCalculatorInput(
            departure="東京",
            destination="新宿",
            transport_type="電車",
            travel_date="2026-05-21",
        )
        assert inp.departure == "東京"
        assert inp.transport_type == "電車"

    def test_normalize_transport_type(self):
        """英語表記の交通手段が正規化されること"""
        from tools.transport_calculator import TransportCalculatorInput
        inp = TransportCalculatorInput(
            departure="東京",
            destination="新宿",
            transport_type="train",
            travel_date="2026-05-21",
        )
        assert inp.transport_type == "電車"

    def test_invalid_transport_type(self):
        """無効な交通手段でValidationErrorが発生すること"""
        from pydantic import ValidationError
        from tools.transport_calculator import TransportCalculatorInput
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="東京",
                destination="新宿",
                transport_type="自転車",
                travel_date="2026-05-21",
            )

    def test_invalid_date_format(self):
        """無効な日付形式でValidationErrorが発生すること"""
        from pydantic import ValidationError
        from tools.transport_calculator import TransportCalculatorInput
        with pytest.raises(ValidationError):
            TransportCalculatorInput(
                departure="東京",
                destination="新宿",
                transport_type="電車",
                travel_date="2026/05/21",
            )


class TestCalculateTransportFare:
    """calculate_transport_fare のテスト"""

    def setup_method(self):
        """各テスト前にキャッシュをリセットする"""
        _reset_cache()

    def test_train_fare_success(self):
        """電車運賃の正常計算（train_fares.json モック）"""
        train_data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(train_data))):
                result = tc.calculate_transport_fare(
                    departure="東京",
                    destination="新宿",
                    transport_type="電車",
                    travel_date="2026-05-21",
                )
        assert result["success"] is True
        assert result["fare"] == 200
        assert result["error_message"] is None

    def test_fixed_fare_bus_success(self):
        """バスの固定運賃の正常取得（fixed_fares.json モック）"""
        fixed_data = {"バス": 220, "タクシー": 730, "飛行機": 15000}
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(fixed_data))):
                result = tc.calculate_transport_fare(
                    departure="A",
                    destination="B",
                    transport_type="バス",
                    travel_date="2026-05-21",
                )
        assert result["success"] is True
        assert result["fare"] == 220

    def test_train_route_not_found(self):
        """存在しない経路でエラーが返ること"""
        train_data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(train_data))):
                result = tc.calculate_transport_fare(
                    departure="東京",
                    destination="大阪",
                    transport_type="電車",
                    travel_date="2026-05-21",
                )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_validation_error_empty_departure(self):
        """空文字の出発地でエラーが返ること"""
        result = tc.calculate_transport_fare(
            departure="",
            destination="新宿",
            transport_type="電車",
            travel_date="2026-05-21",
        )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_validation_error_invalid_transport_type(self):
        """無効な交通手段でエラーが返ること"""
        result = tc.calculate_transport_fare(
            departure="東京",
            destination="新宿",
            transport_type="自転車",
            travel_date="2026-05-21",
        )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_train_fares_file_not_found(self):
        """train_fares.json が存在しない場合にエラーが返ること"""
        with patch("os.path.exists", return_value=False):
            result = tc.calculate_transport_fare(
                departure="東京",
                destination="新宿",
                transport_type="電車",
                travel_date="2026-05-21",
            )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_fixed_fares_file_not_found(self):
        """fixed_fares.json が存在しない場合にエラーが返ること"""
        with patch("os.path.exists", return_value=False):
            result = tc.calculate_transport_fare(
                departure="A",
                destination="B",
                transport_type="バス",
                travel_date="2026-05-21",
            )
        assert result["success"] is False
        assert result["error_message"] is not None

    def test_cache_prevents_reload(self):
        """2回目以降の呼び出しでキャッシュが使用されること"""
        train_data = {"routes": [{"departure": "東京", "destination": "新宿", "fare": 200}]}
        with patch("os.path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(train_data))) as mock_file:
                # 1回目
                tc.calculate_transport_fare("東京", "新宿", "電車", "2026-05-21")
                first_call_count = mock_file.call_count
                # 2回目（キャッシュ済み）
                tc.calculate_transport_fare("東京", "新宿", "電車", "2026-05-21")
                # ファイルオープン回数が増えていないこと
                assert mock_file.call_count == first_call_count
