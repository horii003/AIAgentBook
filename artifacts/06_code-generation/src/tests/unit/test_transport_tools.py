"""交通費計算ツールの単体テスト"""
import json
import pytest
import tools.transport_tools as tt


@pytest.fixture(autouse=True)
def reset_cache():
    """各テスト前にキャッシュをリセットする"""
    tt._train_fares = []
    tt._train_fares_loaded = False
    tt._fixed_fares = {}
    tt._fixed_fares_loaded = False
    yield


@pytest.fixture
def train_fares_file(tmp_path, monkeypatch):
    """テスト用train_fares.jsonを作成する"""
    data = [
        {"departure": "東京", "destination": "大阪", "fare": 13240.0},
        {"departure": "大阪", "destination": "東京", "fare": 13240.0},
    ]
    fares_file = tmp_path / "train_fares.json"
    fares_file.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(tt, "_TRAIN_FARES_PATH", str(fares_file))
    return fares_file


@pytest.fixture
def fixed_fares_file(tmp_path, monkeypatch):
    """テスト用fixed_fares.jsonを作成する"""
    data = {"バス": 500.0, "タクシー": 1000.0, "飛行機": 20000.0}
    fares_file = tmp_path / "fixed_fares.json"
    fares_file.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(tt, "_FIXED_FARES_PATH", str(fares_file))
    return fares_file


class TestCalculateTransportFare:
    def test_registered_route_train(self, train_fares_file):
        """TC-UNIT-001: 登録済み経路（電車）で正しい交通費が返ること"""
        result = calculate_transport_fare_fn("東京", "大阪", "電車", "2026-05-10")
        assert result["success"] is True
        assert result["fare"] == 13240.0
        assert result["not_found"] is False

    def test_bus_fixed_fare(self, fixed_fares_file):
        """TC-UNIT-002: バスの固定運賃が返ること"""
        result = calculate_transport_fare_fn("A", "B", "バス", "2026-05-10")
        assert result["success"] is True
        assert result["fare"] == 500.0

    def test_taxi_fixed_fare(self, fixed_fares_file):
        """タクシーの固定運賃が返ること"""
        result = calculate_transport_fare_fn("A", "B", "タクシー", "2026-05-10")
        assert result["success"] is True
        assert result["fare"] == 1000.0

    def test_airplane_fixed_fare(self, fixed_fares_file):
        """飛行機の固定運賃が返ること"""
        result = calculate_transport_fare_fn("A", "B", "飛行機", "2026-05-10")
        assert result["success"] is True
        assert result["fare"] == 20000.0

    def test_unregistered_route(self, train_fares_file):
        """TC-UNIT-003: 経路未登録時にnot_found=Trueが返ること"""
        result = calculate_transport_fare_fn("未登録駅", "未登録駅", "電車", "2026-05-10")
        assert result["success"] is True
        assert result["not_found"] is True

    def test_invalid_transport_type(self, train_fares_file):
        """TC-UNIT-004: 対応外交通手段でsuccess=Falseが返ること"""
        result = calculate_transport_fare_fn("東京", "大阪", "自転車", "2026-05-10")
        assert result["success"] is False
        assert len(result["error_message"]) > 0

    def test_station_name_normalization(self, train_fares_file):
        """TC-UNIT-005: 駅名の接尾語が正規化されること"""
        result = calculate_transport_fare_fn("東京駅", "大阪駅", "電車", "2026-05-10")
        assert result["success"] is True
        assert result["fare"] == 13240.0

    def test_missing_train_fares_file(self, monkeypatch):
        """TC-UNIT-006: データファイル不存在時にsuccess=Falseが返ること"""
        monkeypatch.setattr(tt, "_TRAIN_FARES_PATH", "nonexistent.json")
        result = calculate_transport_fare_fn("東京", "大阪", "電車", "2026-05-10")
        assert result["success"] is False
        assert len(result["error_message"]) > 0

    def test_invalid_date_format(self, train_fares_file):
        """TC-UNIT-007: 不正な日付形式でsuccess=Falseが返ること"""
        result = calculate_transport_fare_fn("東京", "大阪", "電車", "2026/05/10")
        assert result["success"] is False
        assert len(result["error_message"]) > 0

    def test_cache_used_on_second_call(self, train_fares_file):
        """2回目以降の呼び出しでキャッシュが使用されること"""
        calculate_transport_fare_fn("東京", "大阪", "電車", "2026-05-10")
        assert tt._train_fares_loaded is True
        # キャッシュが使われることを確認（ファイルを削除しても動作する）
        train_fares_file.unlink()
        result = calculate_transport_fare_fn("東京", "大阪", "電車", "2026-05-10")
        assert result["success"] is True


def calculate_transport_fare_fn(departure, destination, transport_type, travel_date):
    """テスト用ラッパー（@toolデコレータをバイパス）"""
    return tt.calculate_transport_fare.__wrapped__(departure, destination, transport_type, travel_date)
