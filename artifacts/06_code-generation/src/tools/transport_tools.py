"""交通費計算ツール

運賃データを検索し、出発地・目的地・交通手段・移動日に基づいて交通費を計算する。
"""
import json
import logging
import os
from strands import tool, ToolContext
from pydantic import ValidationError
from models.data_models import TransportCalculatorInput, TrainRouteRecord
from handlers.error_handler import ErrorHandler

_logger = logging.getLogger(__name__)

# ============ モジュールレベルキャッシュ ============
_train_routes: list = []
_train_routes_loaded: bool = False
_fixed_fares: dict = {}
_fixed_fares_loaded: bool = False

_TRAIN_ROUTES_PATH = "./data/train_routes.json"
_FIXED_FARES_PATH = "./data/fixed_fares.json"

# 固定運賃データの英語→日本語マッピング
_FIXED_FARE_KEY_MAP = {
    "バス": "bus",
    "タクシー": "taxi",
    "飛行機": "airplane",
}


def _load_train_routes() -> tuple:
    """電車経路・運賃データを読み込む。

    Returns:
        tuple[bool, str]: (成功フラグ, エラーメッセージ)
    """
    global _train_routes, _train_routes_loaded
    if not os.path.exists(_TRAIN_ROUTES_PATH):
        msg = ErrorHandler.handle_fare_data_error(FileNotFoundError(_TRAIN_ROUTES_PATH))
        _logger.warning("運賃データファイルが見つかりません: %s", _TRAIN_ROUTES_PATH)
        return (False, msg)
    try:
        with open(_TRAIN_ROUTES_PATH, encoding="utf-8") as f:
            raw = json.load(f)
        # {"routes": [...]} 形式に対応
        routes_data = raw.get("routes", raw) if isinstance(raw, dict) else raw
        _train_routes = [TrainRouteRecord(**r).model_dump() for r in routes_data]
        _train_routes_loaded = True
        _logger.info("電車経路データ読み込み完了: %d件", len(_train_routes))
        return (True, "")
    except Exception as e:
        msg = ErrorHandler.handle_fare_data_error(e)
        _logger.error("電車経路データ読み込みエラー: %s", e, exc_info=True)
        return (False, msg)


def _load_fixed_fares() -> tuple:
    """固定運賃データを読み込む。

    Returns:
        tuple[bool, str]: (成功フラグ, エラーメッセージ)
    """
    global _fixed_fares, _fixed_fares_loaded
    if not os.path.exists(_FIXED_FARES_PATH):
        msg = ErrorHandler.handle_fare_data_error(FileNotFoundError(_FIXED_FARES_PATH))
        _logger.warning("固定運賃データファイルが見つかりません: %s", _FIXED_FARES_PATH)
        return (False, msg)
    try:
        with open(_FIXED_FARES_PATH, encoding="utf-8") as f:
            _fixed_fares = json.load(f)
        _fixed_fares_loaded = True
        _logger.info("固定運賃データ読み込み完了: %s", _fixed_fares)
        return (True, "")
    except Exception as e:
        msg = ErrorHandler.handle_fare_data_error(e)
        _logger.error("固定運賃データ読み込みエラー: %s", e, exc_info=True)
        return (False, msg)


@tool(context=True)
def calculate_transport_fare(
    departure: str,
    destination: str,
    transport_type: str,
    travel_date: str,
    tool_context: ToolContext,
) -> dict:
    """出発地・目的地・交通手段・移動日から交通費を計算する。

    電車の場合は運賃データ（train_routes.json）から経路を検索し運賃を返す。
    バス・タクシー・飛行機の場合は固定運賃データ（fixed_fares.json）から運賃を返す。
    該当経路が存在しない場合はエラーメッセージを返す。

    Args:
        departure: 出発地（正規化済み駅名。「渋谷駅」ではなく「渋谷」の形式）
        destination: 目的地（正規化済み駅名。「渋谷駅」ではなく「渋谷」の形式）
        transport_type: 交通手段。以下のいずれかを指定:
            - "電車"（または "train"）
            - "バス"（または "bus"）
            - "タクシー"（または "taxi"）
            - "飛行機"（または "airplane", "plane"）
        travel_date: 移動日（YYYY-MM-DD 形式。例: "2026-05-17"）
        tool_context: ツールコンテキスト（invocation_stateを含む）

    Returns:
        dict: {
            "success": bool,
            "fare": int | None,
            "message": str | None
        }
    """
    # ステップ1: 入力バリデーション
    try:
        validated = TransportCalculatorInput(
            departure=departure,
            destination=destination,
            transport_type=transport_type,
            travel_date=travel_date,
        )
    except ValidationError as e:
        _logger.error("バリデーションエラー: %s", e, exc_info=True)
        return {"success": False, "fare": None, "message": ErrorHandler.handle_validation_error(e)}

    # ステップ2: 運賃データ読み込み
    if not _train_routes_loaded:
        ok, err_msg = _load_train_routes()
        if not ok:
            return {"success": False, "fare": None, "message": err_msg}

    if not _fixed_fares_loaded:
        ok, err_msg = _load_fixed_fares()
        if not ok:
            return {"success": False, "fare": None, "message": err_msg}

    # ステップ3: 交通手段による分岐
    try:
        if validated.transport_type == "電車":
            # 経路検索
            fare = None
            for route in _train_routes:
                if route["departure"] == validated.departure and route["destination"] == validated.destination:
                    fare = route["fare"]
                    break
            if fare is None:
                raise ValueError(
                    f"経路が見つかりません: {validated.departure} → {validated.destination}"
                )
        else:
            # 固定運賃取得（英語キーで検索）
            en_key = _FIXED_FARE_KEY_MAP.get(validated.transport_type)
            fare = _fixed_fares.get(en_key) if en_key else None
            if fare is None:
                raise ValueError(
                    f"固定運賃が見つかりません: {validated.transport_type}"
                )

        return {"success": True, "fare": fare, "message": None}

    except ValueError as e:
        _logger.warning("経路/運賃が見つかりません: %s", e)
        return {"success": False, "fare": None, "message": str(e)}
    except Exception as e:
        _logger.error("交通費計算エラー: %s", e, exc_info=True)
        return {"success": False, "fare": None, "message": ErrorHandler.handle_calculation_error(e)}
