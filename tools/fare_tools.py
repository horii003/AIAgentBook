"""運賃計算関連のツール"""
import json
import os
from typing import Dict, List
from strands import Agent, tool
from pydantic import ValidationError
from models.data_models import FareData, TrainFareRoute
from handlers.error_handler import ErrorHandler


# グローバル変数として運賃データを保持
_fare_data_cache = None

# エラーハンドラーの初期化
_error_handler = ErrorHandler()


#運賃データの読み込み関数
def load_fare_data() -> dict:
    """
    dataフォルダから運賃データを読み込みます。
    
    Returns:
        dict: {
            "train_fares": List[dict],  # 電車の運賃テーブル
            "fixed_fares": dict          # バス、タクシー、飛行機の固定運賃
        }
    
    Raises:
        FileNotFoundError: 運賃データファイルが見つからない場合
        ValueError: データ形式が不正な場合
    """

    global _fare_data_cache
    
    # 一度読み込んでいればキャッシュをそのまま返す
    if _fare_data_cache is not None:
        return _fare_data_cache
    
    # ファイルパスの設定
    train_fares_path = os.path.join("data", "train_fares.json")
    fixed_fares_path = os.path.join("data", "fixed_fares.json")
    
    # ファイルの存在有無を確認
    #電車運賃のファイル確認
    if not os.path.exists(train_fares_path):
        error_msg = f"電車運賃データファイルが見つかりません: {train_fares_path}"
        context = {"file": train_fares_path, "file_type": "train_fares"}
        user_message = _error_handler.handle_fare_data_error(
            FileNotFoundError(error_msg),
            context
        )
        raise RuntimeError(user_message)

    #固定運賃のファイルの確認
    if not os.path.exists(fixed_fares_path):
        error_msg = f"固定運賃データファイルが見つかりません: {fixed_fares_path}"
        context = {"file": fixed_fares_path, "file_type": "fixed_fares"}
        user_message = _error_handler.handle_fare_data_error(
            FileNotFoundError(error_msg),
            context
        )
        raise RuntimeError(user_message)
    
    #運賃データの読み込み
    try:
        with open(train_fares_path, "r", encoding="utf-8") as f:
            train_data = json.load(f)
        
        with open(fixed_fares_path, "r", encoding="utf-8") as f:
            fixed_data = json.load(f)
        
        # データ形式の検証（Pydanticモデルを使用）
        if "routes" not in train_data:
            raise ValueError("電車運賃データに'routes'キーが存在しません")
        
        # Pydanticモデルでバリデーション
        fare_data_model = FareData(
            train_fares=train_data["routes"],
            fixed_fares=fixed_data
        )
        
        # データをキャッシュ（辞書形式で保持）
        _fare_data_cache = {
            "train_fares": [route.model_dump() for route in fare_data_model.train_fares],
            "fixed_fares": fare_data_model.fixed_fares
        }

        _error_handler.log_info('運賃データを読み込みました')

        return _fare_data_cache
    
    except json.JSONDecodeError as e:
        error_msg = f"JSONファイルの解析に失敗しました: {e}"
        context = {"error_type": "JSONDecodeError", "train_fares_path": train_fares_path, "fixed_fares_path": fixed_fares_path}
        user_message = _error_handler.handle_fare_data_error(
            ValueError(error_msg),
            context
        )
        raise RuntimeError(user_message)


    except ValidationError as e:
        error_msg = f"運賃データの形式が不正です: {e}"
        context = {"error_type": "ValidationError"}
        user_message = _error_handler.handle_fare_data_error(
            ValueError(error_msg),
            context
        )
        raise RuntimeError(user_message)


    except Exception as e:
        error_msg = f"運賃データの読み込み中にエラーが発生しました: {e}"
        context = {"error_type": type(e).__name__}
        user_message = _error_handler.handle_fare_data_error(
            ValueError(error_msg),
            context
        )
        raise RuntimeError(user_message)


#運賃計算用のツール
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
        transport_type: 交通手段（train/bus/taxi/airplane）
        date: 移動日（YYYY-MM-DD形式）
    
    Returns:
        dict: {
            "fare": float,           # 計算された運賃
            "calculation_method": str # 計算方法の説明
        }
    
    Raises:
        ValueError: 経路が運賃データに存在しない場合
    """
    
    # # 駅名から「駅」を削除する正規化処理
    # def normalize_station_name(name: str) -> str:
    #     """駅名から「駅」を削除して正規化する"""
    #     if name.endswith("駅"):
    #         return name[:-1]
    #     return name
    
    # # 出発地と目的地の駅名を正規化
    # departure = normalize_station_name(departure)
    # destination = normalize_station_name(destination)
    
    # 日本語→英語の交通手段変換マッピング
    TRANSPORT_MAPPING = {
        "電車": "train",
        "バス": "bus",
        "タクシー": "taxi",
        "飛行機": "airplane",
    }
    
    # 交通手段の正規化（日本語→英語変換）
    normalized_transport = TRANSPORT_MAPPING.get(
        transport_type, 
        transport_type.lower()
    )
    
    # 有効な交通手段かチェック
    valid_transports = ["train", "bus", "taxi", "airplane"]
    if normalized_transport not in valid_transports:
        error_msg = f"無効な交通手段です: {transport_type}。有効な値: 電車, バス, タクシー, 飛行機, train, bus, taxi, airplane"
        context = {
            "transport_type": transport_type,
            "valid_types_ja": ["電車", "バス", "タクシー", "飛行機"],
            "valid_types_en": valid_transports,
            "departure": departure,
            "destination": destination
        }
        user_message = _error_handler.handle_validation_error(
            ValueError(error_msg),
            context
        )
        raise RuntimeError(user_message)
    
    # 運賃データの読み込み
    fare_data = load_fare_data()

    # 電車の場合の運賃検索
    if normalized_transport == "train":
        # 運賃テーブルから該当する経路を検索
        for route in fare_data["train_fares"]:
            if route["departure"] == departure and route["destination"] == destination:
                return {
                    "fare": float(route["fare"]),
                    "calculation_method": f"電車運賃テーブルから取得: {departure} → {destination}"
                }
        
        # 経路が見つからない場合
        error_msg = f"電車の運賃データに該当する経路が見つかりません: {departure} → {destination}"
        context = {
            "departure": departure,
            "destination": destination,
            "transport_type": normalized_transport,
            "date": date
        }
        user_message = _error_handler.handle_calculation_error(
            ValueError(error_msg),
            context
        )
        raise RuntimeError(user_message)
    

    # バス、タクシー、飛行機の場合の運賃検索（固定運賃）
    else:
        fare = fare_data["fixed_fares"][normalized_transport]
        transport_name_map = {
            "bus": "バス",
            "taxi": "タクシー",
            "airplane": "飛行機"
        }
        return {
            "fare": float(fare),
            "calculation_method": f"{transport_name_map[normalized_transport]}の固定運賃"
        }
