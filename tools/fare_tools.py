"""運賃計算関連のツール"""
import json
import os
from typing import Tuple
from strands import tool
from pydantic import ValidationError
from models.data_models import FareData, TrainFareRoute, FareCalculationInput
from handlers.error_handler import ErrorHandler


# エラーハンドラーの初期化
_error_handler = ErrorHandler()

#運賃データの読み込み関数
def load_fare_data():
    """
    dataフォルダから運賃データを読み込みます。
    
    Returns:
        Tuple[bool, dict | str]: (成功フラグ, データまたはエラーメッセージ)
            - 成功時: (True, 運賃データdict)
            - エラー時: (False, ユーザー向けエラーメッセージstr)
    """

    # ファイルパスの設定
    train_fares_path = os.path.join("data", "train_fares.json")
    fixed_fares_path = os.path.join("data", "fixed_fares.json")
    
    # ファイルの存在有無を確認
    #電車運賃のファイル確認
    if not os.path.exists(train_fares_path):
        e = FileNotFoundError(f"電車運賃データファイルが見つかりません: {train_fares_path}")
        context = {"file": train_fares_path, "file_type": "train_fares"}
        error_message = _error_handler.handle_fare_data_error(e, context)
        return False, error_message

    #固定運賃のファイルの確認
    if not os.path.exists(fixed_fares_path):
        e = FileNotFoundError(f"固定運賃データファイルが見つかりません: {fixed_fares_path}")
        context = {"file": fixed_fares_path, "file_type": "fixed_fares"}
        error_message = _error_handler.handle_fare_data_error(e, context)
        return False, error_message
        
    
    #運賃データの読み込み
    try:
        with open(train_fares_path, "r", encoding="utf-8") as f:
            train_data = json.load(f)
        
        with open(fixed_fares_path, "r", encoding="utf-8") as f:
            fixed_data = json.load(f)
        
        # Pydanticモデルでバリデーション（データ形式の検証も含む）
        fare_data_model = FareData(
            train_fares=train_data.get("routes", []),
            fixed_fares=fixed_data
        )
        
        # バリデーション済みデータを辞書形式に変換
        dict_fare_data = {
            "train_fares": [route.model_dump() for route in fare_data_model.train_fares],
            "fixed_fares": fare_data_model.fixed_fares
        }

        _error_handler.log_info('運賃データを読み込みました')

        return True, dict_fare_data
    
    except json.JSONDecodeError as e:
        context = {"error_type": "JSONDecodeError", "train_fares_path": train_fares_path, "fixed_fares_path": fixed_fares_path}
        error_message = _error_handler.handle_fare_data_error(e, context)
        return False, error_message

    except Exception as e:
        context = {"error_type": type(e).__name__}
        error_message = _error_handler.handle_fare_data_error(e, context)
        return False, error_message


@tool
def calculate_fare(
    departure: str,
    destination: str,
    transport_type: str,
    date: str
) -> dict:
    """
    経路の交通費を計算します。
    
    Args:
        departure: 出発地
        destination: 目的地
        transport_type: 交通手段（train/bus/taxi/airplane または 電車/バス/タクシー/飛行機）
        date: 移動日（YYYY-MM-DD形式）
    
    Returns:
        dict: {
            "success": bool,         # 成功フラグ
            "fare": float,           # 計算された運賃（エラー時は0）
            "calculation_method": str, # 計算方法の説明（エラー時は空文字列）
            "message": str           # 結果メッセージ（エラー時はエラーメッセージ）
        }
    """
    # ツール呼び出しログ
    _error_handler.log_info(
        "calculate_fareツールが呼び出されました",
        context={
            "departure": departure,
            "destination": destination,
            "transport_type": transport_type,
            "date": date
        }
    )
    
    # Pydanticモデルで入力をバリデーション
    try:
        input_data = FareCalculationInput(
            departure=departure,
            destination=destination,
            transport_type=transport_type,
            date=date
        )
    except ValidationError as e:
        context = {
            "departure": departure,
            "destination": destination,
            "transport_type": transport_type,
            "date": date
        }
        error_message = _error_handler.handle_validation_error(e, context)
        return {
            "success": False,
            "fare": 0,
            "calculation_method": "",
            "message": error_message
        }
    
    # 正規化された交通手段を使用
    normalized_transport = input_data.transport_type
    
    # 運賃データの読み込み関数の利用
    success, fare_data = load_fare_data()
    
    # エラーが発生した場合
    if not success:
        return {
            "success": False,
            "fare": 0,
            "calculation_method": "",
            "message": fare_data  
        }

    # 電車の場合の運賃検索
    if normalized_transport == "train":
        # 運賃テーブルから該当する経路を検索
        for route in fare_data["train_fares"]:
            if route["departure"] == departure and route["destination"] == destination:
                _error_handler.log_info(
                    f"運賃を計算しました: {departure} → {destination} = ¥{route['fare']}"
                )
                return {
                    "success": True,
                    "fare": float(route["fare"]),
                    "calculation_method": f"電車運賃テーブルから取得: {departure} → {destination}",
                    "message": f"運賃を計算しました: ¥{route['fare']}"
                }
        
        # 経路が見つからない場合
        e = ValueError(f"電車の運賃データに該当する経路が見つかりません: {departure} → {destination}")
        context = {
            "departure": departure,
            "destination": destination,
            "transport_type": normalized_transport,
            "date": date
        }
        error_message = _error_handler.handle_calculation_error(e, context)
        return {
            "success": False,
            "fare": 0,
            "calculation_method": "",
            "message": error_message
        }
    
    # バス、タクシー、飛行機の場合の運賃検索（固定運賃）
    else:
        fare = fare_data["fixed_fares"][normalized_transport]
        transport_name_map = {
            "bus": "バス",
            "taxi": "タクシー",
            "airplane": "飛行機"
        }
        _error_handler.log_info(f"運賃を計算しました: {transport_name_map[normalized_transport]} = ¥{fare}"
        )
        return {
            "success": True,
            "fare": float(fare),
            "calculation_method": f"{transport_name_map[normalized_transport]}の固定運賃",
            "message": f"運賃を計算しました: ¥{fare}"
        }
