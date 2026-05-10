"""交通費計算ツール

出発地・目的地・交通手段・移動日をもとに交通費を計算するツール関数を提供する。
"""
import json
import logging
import os
from pydantic import ValidationError
from strands import tool
from models.data_models import TransportCalculatorInput, TrainFareRecord
from handlers.error_handler import ErrorHandler

_logger = logging.getLogger(__name__)

# データファイルパス
_TRAIN_FARES_PATH = "data/train_fares.json"
_FIXED_FARES_PATH = "data/fixed_fares.json"

# モジュールレベルキャッシュ（空リストによる未ロード判定禁止: R9.12.4）
_train_fares: list[dict] = []
_train_fares_loaded: bool = False
_fixed_fares: dict = {}
_fixed_fares_loaded: bool = False


def _load_train_fares() -> tuple[bool, str]:
    """train_fares.jsonをモジュールレベルキャッシュに読み込む（初回のみ）

    Returns:
        tuple[bool, str]: (成功フラグ, エラーメッセージ)
    """
    global _train_fares, _train_fares_loaded
    if not os.path.exists(_TRAIN_FARES_PATH):
        _logger.warning("データファイルが見つかりません: %s", _TRAIN_FARES_PATH)
        return (False, ErrorHandler.handle_fare_data_error(FileNotFoundError(_TRAIN_FARES_PATH)))
    try:
        with open(_TRAIN_FARES_PATH, encoding="utf-8") as f:
            raw_data = json.load(f)
        # train_fares.jsonは {"routes": [...]} 形式
        records = raw_data["routes"] if isinstance(raw_data, dict) and "routes" in raw_data else raw_data
        validated = [TrainFareRecord(**record).model_dump() for record in records]
        _train_fares = validated
        _train_fares_loaded = True
        _logger.info("交通費データファイルを読み込みました: %s (%d件)", _TRAIN_FARES_PATH, len(_train_fares))
        return (True, "")
    except Exception as e:
        _logger.error("データファイルの読み込みに失敗しました: %s", _TRAIN_FARES_PATH, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))


def _load_fixed_fares() -> tuple[bool, str]:
    """fixed_fares.jsonをモジュールレベルキャッシュに読み込む（初回のみ）

    Returns:
        tuple[bool, str]: (成功フラグ, エラーメッセージ)
    """
    global _fixed_fares, _fixed_fares_loaded
    if not os.path.exists(_FIXED_FARES_PATH):
        _logger.warning("データファイルが見つかりません: %s", _FIXED_FARES_PATH)
        return (False, ErrorHandler.handle_fare_data_error(FileNotFoundError(_FIXED_FARES_PATH)))
    try:
        with open(_FIXED_FARES_PATH, encoding="utf-8") as f:
            _fixed_fares = json.load(f)
        _fixed_fares_loaded = True
        _logger.info("固定運賃データファイルを読み込みました: %s", _FIXED_FARES_PATH)
        return (True, "")
    except Exception as e:
        _logger.error("データファイルの読み込みに失敗しました: %s", _FIXED_FARES_PATH, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))


@tool
def calculate_transport_fare(
    departure: str,
    destination: str,
    transport_type: str,
    travel_date: str,
) -> dict:
    """出発地・目的地・交通手段・移動日をもとに交通費を計算する。

    電車の場合は経路テーブル（data/train_fares.json）を参照し、
    バス・タクシー・飛行機の場合は固定運賃データ（data/fixed_fares.json）を参照する。
    経路が登録されていない場合は not_found=True を返す。

    Args:
        departure: 出発地（駅名・バス停名等。「駅」「バス停」「空港」等の接尾語は自動除去される）
        destination: 目的地（駅名・バス停名等。「駅」「バス停」「空港」等の接尾語は自動除去される）
        transport_type: 交通手段。以下のいずれかを指定する（表記ゆれは自動正規化される）:
            - 「電車」「train」「電鉄」「鉄道」→ 電車
            - 「バス」「bus」→ バス
            - 「タクシー」「taxi」「cab」→ タクシー
            - 「飛行機」「airplane」「plane」「flight」「航空」→ 飛行機
        travel_date: 移動日（YYYY-MM-DD形式）

    Returns:
        dict: 以下のキーを持つ辞書:
            - success (bool): 処理成功フラグ
            - fare (float): 交通費（円）
            - calculation_basis (str): 計算根拠
            - not_found (bool): 経路未登録フラグ
            - error_message (str): エラーメッセージ
    """
    _empty = {"success": False, "fare": 0.0, "calculation_basis": "", "not_found": False, "error_message": ""}

    # 入力バリデーション
    try:
        validated = TransportCalculatorInput(
            departure=departure,
            destination=destination,
            transport_type=transport_type,
            travel_date=travel_date,
        )
    except ValidationError as e:
        _logger.error("バリデーションエラーが発生しました", exc_info=True)
        return {**_empty, "error_message": ErrorHandler.handle_validation_error(e)}

    try:
        dep = validated.departure
        dst = validated.destination
        t_type = validated.transport_type

        # データ読み込み（キャッシュ未ロード時のみ）
        if t_type == "電車":
            if not _train_fares_loaded:
                ok, err = _load_train_fares()
                if not ok:
                    return {**_empty, "error_message": err}
            # 経路テーブル検索
            for record in _train_fares:
                if record["departure"] == dep and record["destination"] == dst:
                    fare = record["fare"]
                    basis = f"経路テーブル参照: {dep}→{dst} 電車 ¥{fare:,.0f}"
                    _logger.info("交通費計算完了: %s→%s %s ¥%s", dep, dst, t_type, fare)
                    return {"success": True, "fare": fare, "calculation_basis": basis, "not_found": False, "error_message": ""}
            # 未登録
            _logger.info("経路未登録: %s→%s %s", dep, dst, t_type)
            return {"success": True, "fare": 0.0, "calculation_basis": "", "not_found": True, "error_message": ""}
        else:
            if not _fixed_fares_loaded:
                ok, err = _load_fixed_fares()
                if not ok:
                    return {**_empty, "error_message": err}
            if t_type in _fixed_fares:
                fare = _fixed_fares[t_type]
                basis = f"固定運賃参照: {t_type} ¥{fare:,.0f}"
                _logger.info("交通費計算完了: %s→%s %s ¥%s", dep, dst, t_type, fare)
                return {"success": True, "fare": fare, "calculation_basis": basis, "not_found": False, "error_message": ""}
            _logger.info("経路未登録: %s→%s %s", dep, dst, t_type)
            return {"success": True, "fare": 0.0, "calculation_basis": "", "not_found": True, "error_message": ""}

    except Exception as e:
        _logger.error("交通費計算中に予期しないエラーが発生しました", exc_info=True)
        return {**_empty, "error_message": ErrorHandler.handle_calculation_error(e)}
