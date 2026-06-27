"""交通費計算ツール

運賃データを参照し、出発地・目的地・交通手段に基づいて交通費を自動計算する。
"""
import json
import logging
import os

from dateutil.relativedelta import relativedelta
from datetime import datetime
from pydantic import ValidationError
from strands import tool, ToolContext

from handlers.error_handler import ErrorHandler
from models.data_models import RouteData, TransportCalculatorInput
from config.settings import settings

_logger = logging.getLogger(__name__)

# ファイルパス定数
_TRAIN_FARES_PATH = "data/train_fares.json"
_FIXED_FARES_PATH = "data/fixed_fares.json"

# キャッシュ変数（R9.12.4準拠: 空コンテナ判定禁止）
_train_fares: list = []
_train_fares_loaded: bool = False

_fixed_fares: dict = {}
_fixed_fares_loaded: bool = False

# 固定運賃データの英語キー→日本語交通手段マッピング
_TRANSPORT_TYPE_TO_KEY = {
    "バス": "bus",
    "タクシー": "taxi",
    "飛行機": "airplane",
}


def _load_train_fares() -> tuple[bool, str]:
    """電車運賃データを読み込む。

    Returns:
        tuple[bool, str]: (成功フラグ, エラーメッセージ)
    """
    global _train_fares, _train_fares_loaded

    if _train_fares_loaded:
        return (True, "")

    if not os.path.exists(_TRAIN_FARES_PATH):
        _logger.warning("運賃データファイルが見つかりません: %s", _TRAIN_FARES_PATH)
        return (False, ErrorHandler.handle_fare_data_error(FileNotFoundError(_TRAIN_FARES_PATH)))

    try:
        with open(_TRAIN_FARES_PATH, encoding="utf-8") as f:
            data = json.load(f)

        # train_fares.jsonは {"routes": [...]} 形式
        routes = data.get("routes", data) if isinstance(data, dict) else data

        validated = []
        for item in routes:
            validated.append(RouteData(**item))
        _train_fares = validated
        _train_fares_loaded = True
        _logger.info("電車運賃データを読み込みました: %d件", len(_train_fares))
        return (True, "")
    except Exception as e:
        _logger.error("運賃データ読み込みエラー: %s", _TRAIN_FARES_PATH, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))


def _load_fixed_fares() -> tuple[bool, str]:
    """固定運賃データを読み込む。

    Returns:
        tuple[bool, str]: (成功フラグ, エラーメッセージ)
    """
    global _fixed_fares, _fixed_fares_loaded

    if _fixed_fares_loaded:
        return (True, "")

    if not os.path.exists(_FIXED_FARES_PATH):
        _logger.warning("固定運賃データファイルが見つかりません: %s", _FIXED_FARES_PATH)
        return (False, ErrorHandler.handle_fare_data_error(FileNotFoundError(_FIXED_FARES_PATH)))

    try:
        with open(_FIXED_FARES_PATH, encoding="utf-8") as f:
            data = json.load(f)

        _fixed_fares = data
        _fixed_fares_loaded = True
        _logger.info("固定運賃データを読み込みました: %d件", len(_fixed_fares))
        return (True, "")
    except Exception as e:
        _logger.error("固定運賃データ読み込みエラー: %s", _FIXED_FARES_PATH, exc_info=True)
        return (False, ErrorHandler.handle_fare_data_error(e))


@tool(context=True)
def calculate_transportation_cost(
    departure: str,
    destination: str,
    transport_type: str,
    travel_date: str,
    tool_context: ToolContext,
) -> dict:
    """出発地・目的地・交通手段・移動日に基づいて交通費を自動計算する。

    電車の場合は経路テーブルから運賃を検索し、バス・タクシー・飛行機の場合は固定運賃を返却する。

    Args:
        departure: 出発地（駅名・場所名）
        destination: 目的地（駅名・場所名）
        transport_type: 交通手段（電車/バス/タクシー/飛行機）
        travel_date: 移動日（YYYY-MM-DD形式）

    Returns:
        dict: {
            "success": bool,
            "fare": Optional[int],
            "error_message": Optional[str],
            "is_expired": Optional[bool]
        }
    """
    _logger.info(
        "交通費計算開始: 出発地=%s, 目的地=%s, 交通手段=%s",
        departure, destination, transport_type,
    )

    # 入力バリデーション
    try:
        validated = TransportCalculatorInput(
            departure=departure,
            destination=destination,
            transport_type=transport_type,
            travel_date=travel_date,
        )
    except ValidationError as e:
        _logger.error("入力バリデーションエラー", exc_info=True)
        return {
            "success": False,
            "fare": None,
            "error_message": ErrorHandler.handle_validation_error(e),
            "is_expired": None,
        }

    # 申請期限チェック
    application_date = tool_context.invocation_state.get("application_date")
    is_expired = False
    if application_date:
        try:
            app_dt = datetime.strptime(application_date, "%Y-%m-%d")
            travel_dt = datetime.strptime(validated.travel_date, "%Y-%m-%d")
            deadline_months = settings.transportation_expense.deadline_months
            deadline_dt = app_dt - relativedelta(months=deadline_months)
            if travel_dt < deadline_dt:
                is_expired = True
                _logger.warning(
                    "申請期限超過: 移動日=%s, 申請日=%s",
                    validated.travel_date, application_date,
                )
        except Exception:
            pass

    # 交通手段による分岐
    try:
        if validated.transport_type == "電車":
            ok, err = _load_train_fares()
            if not ok:
                return {"success": False, "fare": None, "error_message": err, "is_expired": None}

            fare = None
            for route in _train_fares:
                if route.departure == validated.departure and route.destination == validated.destination:
                    fare = route.fare
                    break

            if fare is None:
                _logger.info(
                    "経路未登録: 出発地=%s, 目的地=%s（ユーザーに金額入力を依頼）",
                    validated.departure, validated.destination,
                )
                return {
                    "success": False,
                    "fare": None,
                    "error_message": (
                        f"{validated.departure}→{validated.destination}の経路が登録されていないため"
                        "自動計算できません。実際にかかった金額をユーザーに確認してください。"
                    ),
                    "is_expired": is_expired,
                }

        else:
            ok, err = _load_fixed_fares()
            if not ok:
                return {"success": False, "fare": None, "error_message": err, "is_expired": None}

            # 日本語交通手段→英語キーに変換して参照
            fare_key = _TRANSPORT_TYPE_TO_KEY.get(validated.transport_type)
            if fare_key is None or fare_key not in _fixed_fares:
                return {
                    "success": False,
                    "fare": None,
                    "error_message": "交通手段未登録のため自動計算不可。ユーザーに金額確認を依頼",
                    "is_expired": is_expired,
                }
            fare = _fixed_fares[fare_key]

        _logger.info("交通費計算完了: 金額=%d円", fare)
        return {"success": True, "fare": fare, "error_message": None, "is_expired": is_expired}

    except Exception as e:
        _logger.error("交通費計算エラー", exc_info=True)
        return {
            "success": False,
            "fare": None,
            "error_message": ErrorHandler.handle_calculation_error(e),
            "is_expired": None,
        }
