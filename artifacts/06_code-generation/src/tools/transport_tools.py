"""交通費計算ツール

電車・バス・タクシー・飛行機の運賃を計算する。
"""

import json
import logging
from pathlib import Path

from pydantic import ValidationError
from strands import tool

from handlers.error_handler import ErrorHandler
from models.data_models import TrainRouteRecord, TransportCalculatorInput

_logger = logging.getLogger(__name__)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# モジュールレベルキャッシュ（初期化フラグ管理）
_train_routes: list[dict] = []
_train_routes_loaded: bool = False
_fixed_fares: dict[str, int] = {}
_fixed_fares_loaded: bool = False


def _load_train_routes() -> tuple[bool, str]:
    """電車経路データを読み込む（キャッシュ付き）"""
    global _train_routes, _train_routes_loaded
    file_path = _DATA_DIR / "train_fares.json"
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        # バリデーション
        routes = []
        for record in data.get("routes", []):
            validated = TrainRouteRecord(**record)
            routes.append(validated.model_dump())
        _train_routes = routes
        _train_routes_loaded = True
        return (True, "")
    except FileNotFoundError as e:
        _logger.error("電車経路データファイルが見つかりません: %s", e, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))
    except Exception as e:
        _logger.error("電車経路データ読み込みエラー: %s", e, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))


def _load_fixed_fares() -> tuple[bool, str]:
    """固定運賃データを読み込む（キャッシュ付き）"""
    global _fixed_fares, _fixed_fares_loaded
    file_path = _DATA_DIR / "fixed_fares.json"
    try:
        with open(file_path, encoding="utf-8") as f:
            _fixed_fares = json.load(f)
        _fixed_fares_loaded = True
        return (True, "")
    except FileNotFoundError as e:
        _logger.error("固定運賃データファイルが見つかりません: %s", e, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))
    except Exception as e:
        _logger.error("固定運賃データ読み込みエラー: %s", e, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))


# 交通手段→固定運賃キーのマッピング
_TRANSPORT_TYPE_TO_KEY = {
    "バス": "bus",
    "タクシー": "taxi",
    "飛行機": "airplane",
}


@tool
def calculate_transport_fare(
    departure: str, destination: str, transport_type: str, travel_date: str
) -> dict:
    """交通費を計算する。

    Args:
        departure: 出発地（駅名）
        destination: 目的地（駅名）
        transport_type: 交通手段（電車/バス/タクシー/飛行機）
        travel_date: 移動日（YYYY-MM-DD形式）
    """
    # バリデーション
    try:
        validated = TransportCalculatorInput(
            departure=departure,
            destination=destination,
            transport_type=transport_type,
            travel_date=travel_date,
        )
    except ValidationError as e:
        _logger.error("バリデーションエラー: %s", e, exc_info=True)
        return {
            "success": False,
            "fare": None,
            "error_message": ErrorHandler.handle_validation_error(e),
        }

    normalized_type = validated.transport_type

    # 電車の場合: 経路テーブルから検索
    if normalized_type == "電車":
        if not _train_routes_loaded:
            ok, err_msg = _load_train_routes()
            if not ok:
                return {"success": False, "fare": None, "error_message": err_msg}

        for route in _train_routes:
            if (
                route["departure"] == validated.departure
                and route["destination"] == validated.destination
            ):
                return {"success": True, "fare": route["fare"], "error_message": None}

        return {
            "success": False,
            "fare": None,
            "error_message": f"経路が見つかりません: {validated.departure} → {validated.destination}。手動で金額を入力してください。",
        }

    # バス・タクシー・飛行機の場合: 固定運賃
    if not _fixed_fares_loaded:
        ok, err_msg = _load_fixed_fares()
        if not ok:
            return {"success": False, "fare": None, "error_message": err_msg}

    fare_key = _TRANSPORT_TYPE_TO_KEY.get(normalized_type)
    if fare_key and fare_key in _fixed_fares:
        return {"success": True, "fare": _fixed_fares[fare_key], "error_message": None}

    return {
        "success": False,
        "fare": None,
        "error_message": ErrorHandler.handle_calculation_error(
            ValueError(f"未対応の交通手段: {normalized_type}")
        ),
    }
