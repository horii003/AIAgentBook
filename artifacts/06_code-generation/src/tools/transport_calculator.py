"""交通費計算ツール。

移動情報（出発地・目的地・交通手段）から交通費を自動計算する。
電車は電車経路テーブル（data/train_fares.json）を検索し、
バス・タクシー・飛行機は固定運賃データ（data/fixed_fares.json）を参照する。
"""
import json
import logging
import os
from typing import Literal, Optional

from pydantic import BaseModel, Field, ValidationError, field_validator
from strands import tool

from handlers.error_handler import ErrorHandler
from models.data_models import normalize_transport_type, validate_date_format

_logger = logging.getLogger(__name__)

# データファイルパス
_TRAIN_FARES_PATH = "data/train_fares.json"
_FIXED_FARES_PATH = "data/fixed_fares.json"

# モジュールレベルキャッシュ
_train_routes: list = []
_train_routes_loaded: bool = False
_fixed_fares: dict = {}
_fixed_fares_loaded: bool = False


# ============ データモデル ============

class TransportCalculatorInput(BaseModel):
    """calculate_transport_fare ツールの入力バリデーション。"""

    departure: str = Field(..., min_length=1, description="出発地（正規化済み駅名・地点名）")
    destination: str = Field(..., min_length=1, description="目的地（正規化済み駅名・地点名）")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(
        ..., description="交通手段"
    )
    travel_date: str = Field(..., description="移動日（YYYY-MM-DD形式）")

    _validate_transport_type = field_validator("transport_type", mode="before")(
        classmethod(normalize_transport_type)
    )
    _validate_travel_date = field_validator("travel_date", mode="before")(
        classmethod(validate_date_format)
    )


class TransportCalculatorOutput(BaseModel):
    """calculate_transport_fare ツールの出力スキーマ。"""

    success: bool = Field(..., description="計算成否フラグ")
    fare: Optional[int] = Field(None, ge=0, description="計算済み運賃（円）。正常時のみ設定")
    error_message: Optional[str] = Field(None, description="エラーメッセージ。エラー時のみ設定")


class TrainFareData(BaseModel):
    """電車経路データの1レコード。"""

    departure: str = Field(..., min_length=1, description="出発地（正規化済み駅名）")
    destination: str = Field(..., min_length=1, description="目的地（正規化済み駅名）")
    fare: int = Field(..., ge=0, description="運賃（円）")


# ============ データ読み込み関数 ============

def _load_train_fares() -> tuple:
    """電車経路データを読み込む。

    Returns:
        tuple: (True, "") 成功時、(False, エラーメッセージ) 失敗時
    """
    global _train_routes, _train_routes_loaded

    if _train_routes_loaded:
        return (True, "")

    if not os.path.exists(_TRAIN_FARES_PATH):
        _logger.warning("データファイルが見つかりません: %s", _TRAIN_FARES_PATH)
        return (False, ErrorHandler.handle_fare_data_error(FileNotFoundError(_TRAIN_FARES_PATH)))

    try:
        with open(_TRAIN_FARES_PATH, encoding="utf-8") as f:
            data = json.load(f)
        routes = [TrainFareData(**r) for r in data.get("routes", [])]
        _train_routes = routes
        _train_routes_loaded = True
        _logger.info("電車経路データを読み込みました: %d件", len(_train_routes))
        return (True, "")
    except Exception as e:
        _logger.error("データ読み込みエラー: %s", _TRAIN_FARES_PATH, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))


def _load_fixed_fares() -> tuple:
    """固定運賃データを読み込む。

    Returns:
        tuple: (True, "") 成功時、(False, エラーメッセージ) 失敗時
    """
    global _fixed_fares, _fixed_fares_loaded

    if _fixed_fares_loaded:
        return (True, "")

    if not os.path.exists(_FIXED_FARES_PATH):
        _logger.warning("データファイルが見つかりません: %s", _FIXED_FARES_PATH)
        return (False, ErrorHandler.handle_fare_data_error(FileNotFoundError(_FIXED_FARES_PATH)))

    try:
        with open(_FIXED_FARES_PATH, encoding="utf-8") as f:
            data = json.load(f)
        _fixed_fares = data
        _fixed_fares_loaded = True
        _logger.info("固定運賃データを読み込みました: %d件", len(_fixed_fares))
        return (True, "")
    except Exception as e:
        _logger.error("データ読み込みエラー: %s", _FIXED_FARES_PATH, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))


# ============ ツール関数 ============

@tool
def calculate_transport_fare(
    departure: str,
    destination: str,
    transport_type: str,
    travel_date: str,
) -> dict:
    """移動情報（出発地・目的地・交通手段）から交通費を計算する。

    電車の場合は電車経路テーブル（data/train_fares.json）を検索し、
    バス・タクシー・飛行機の場合は固定運賃データ（data/fixed_fares.json）を参照する。

    Args:
        departure: 出発地（正規化済み駅名・地点名）。空文字不可。
        destination: 目的地（正規化済み駅名・地点名）。空文字不可。
        transport_type: 交通手段。許容値: "電車", "バス", "タクシー", "飛行機"。
            英語表記（"train", "bus", "taxi", "airplane"/"plane"）も自動正規化される。
        travel_date: 移動日（YYYY-MM-DD形式）。申請期限チェックに使用。

    Returns:
        dict: 以下のキーを持つ辞書:
            - success (bool): 計算成否フラグ
            - fare (int | None): 計算済み運賃（円）。正常時のみ設定。
            - error_message (str | None): エラーメッセージ。エラー時のみ設定。
    """
    # 入力バリデーション
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

    # 交通手段に応じて運賃を計算
    try:
        if validated.transport_type == "電車":
            return _calculate_train_fare(validated.departure, validated.destination)
        else:
            return _calculate_fixed_fare(validated.transport_type)
    except Exception as e:
        _logger.error(
            "予期しないエラー（運賃計算）: %s→%s",
            departure,
            destination,
            exc_info=True,
        )
        return {
            "success": False,
            "fare": None,
            "error_message": ErrorHandler.handle_calculation_error(e),
        }


def _calculate_train_fare(departure: str, destination: str) -> dict:
    """電車運賃を計算する。

    Args:
        departure: 出発地
        destination: 目的地

    Returns:
        dict: 計算結果辞書
    """
    ok, err_msg = _load_train_fares()
    if not ok:
        return {"success": False, "fare": None, "error_message": err_msg}

    # 経路を検索
    for route in _train_routes:
        if route.departure == departure and route.destination == destination:
            _logger.info(
                "運賃計算成功: %s→%s(電車) = %d円", departure, destination, route.fare
            )
            return {"success": True, "fare": route.fare, "error_message": None}

    # 経路が見つからない場合
    _logger.warning("経路データが見つかりません: %s→%s", departure, destination)
    error_msg = (
        f"指定された経路（{departure}→{destination}）の運賃データが見つかりませんでした。"
        "運賃を直接入力してください。"
    )
    return {"success": False, "fare": None, "error_message": error_msg}


def _calculate_fixed_fare(transport_type: str) -> dict:
    """固定運賃を取得する。

    Args:
        transport_type: 交通手段

    Returns:
        dict: 計算結果辞書
    """
    ok, err_msg = _load_fixed_fares()
    if not ok:
        return {"success": False, "fare": None, "error_message": err_msg}

    if transport_type not in _fixed_fares:
        error_msg = f"指定された交通手段（{transport_type}）の運賃データが見つかりませんでした。"
        return {"success": False, "fare": None, "error_message": error_msg}

    fare = _fixed_fares[transport_type]
    _logger.info("運賃計算成功: %s = %d円", transport_type, fare)
    return {"success": True, "fare": fare, "error_message": None}
