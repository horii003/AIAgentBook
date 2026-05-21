"""データモデルの定義

業務ドメインに応じたPydanticモデルを定義する。
各モデルはツール入力、エージェント状態、マスタデータの型安全性を保証する。
"""
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator
from dateutil import parser as dateutil_parser


# ============ 共通バリデーター ============

def validate_station_name(v: str) -> str:
    """駅名の正規化バリデーター。末尾の「駅」を除去する。

    Args:
        v: 駅名文字列

    Returns:
        正規化済み駅名

    Raises:
        ValueError: 空文字列の場合
    """
    if not v or not v.strip():
        raise ValueError("駅名を入力してください。")
    return v.removesuffix("駅").strip()


def normalize_transport_type(v: str) -> str:
    """交通手段の正規化バリデーター。英語表記を日本語に変換する。

    Args:
        v: 交通手段文字列

    Returns:
        正規化済み交通手段

    Raises:
        ValueError: マッピングに存在しない値の場合
    """
    mapping = {
        "train": "電車", "電車": "電車",
        "bus": "バス", "バス": "バス",
        "taxi": "タクシー", "タクシー": "タクシー",
        "airplane": "飛行機", "plane": "飛行機", "飛行機": "飛行機",
    }
    normalized = mapping.get(v)
    if normalized is None:
        raise ValueError(f"交通手段のエラー: 電車・バス・タクシー・飛行機のいずれかを指定してください。（入力値: {v}）")
    return normalized


def validate_date_format(v: str) -> str:
    """日付形式のバリデーター。YYYY-MM-DD 形式に正規化する。

    Args:
        v: 日付文字列

    Returns:
        YYYY-MM-DD 形式の日付文字列

    Raises:
        ValueError: パース不能な文字列の場合
    """
    try:
        return dateutil_parser.parse(v).strftime("%Y-%m-%d")
    except Exception:
        raise ValueError(f"日付の形式が正しくありません（YYYY-MM-DD 形式で入力してください）。（入力値: {v}）")


# ============ エージェント状態モデル ============

class InvocationState(BaseModel):
    """オーケストレーターから子エージェントへ渡す共有状態"""
    applicant_name: str = Field(..., description="申請者名")
    application_date: str = Field(..., description="申請日（YYYY-MM-DD）")
    session_id: str = Field(..., description="セッションID（子エージェントのファクトリで消費）")


# ============ マスタデータモデル ============

class TrainRouteRecord(BaseModel):
    """電車経路・運賃データ（train_routes.json）の1レコード"""
    departure: str = Field(..., min_length=1, description="出発駅")
    destination: str = Field(..., min_length=1, description="到着駅")
    fare: int = Field(..., gt=0, description="運賃（円）")


# ============ ツール入力モデル ============

def _cls_validate_station_name(cls, v: str) -> str:
    """classmethod ラッパー: validate_station_name"""
    return validate_station_name(v)


def _cls_normalize_transport_type(cls, v: str) -> str:
    """classmethod ラッパー: normalize_transport_type"""
    return normalize_transport_type(v)


def _cls_validate_date_format(cls, v: str) -> str:
    """classmethod ラッパー: validate_date_format"""
    return validate_date_format(v)


class TransportCalculatorInput(BaseModel):
    """交通費計算ツール（calculate_transport_fare）の入力パラメータ"""
    departure: str = Field(..., min_length=1, description="出発地（正規化済み駅名）")
    destination: str = Field(..., min_length=1, description="目的地（正規化済み駅名）")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(..., description="交通手段")
    travel_date: str = Field(..., description="移動日（YYYY-MM-DD）")

    _validate_departure = field_validator("departure", mode="before")(classmethod(_cls_validate_station_name))
    _validate_destination = field_validator("destination", mode="before")(classmethod(_cls_validate_station_name))
    _validate_transport_type = field_validator("transport_type", mode="before")(classmethod(_cls_normalize_transport_type))
    _validate_travel_date = field_validator("travel_date", mode="before")(classmethod(_cls_validate_date_format))


class ExpenseItem(BaseModel):
    """経費明細の1件"""
    purchase_date: str = Field(..., description="購入日（YYYY-MM-DD）")
    store_name: str = Field(..., min_length=1, description="店舗名")
    item_name: str = Field(..., min_length=1, description="品目")
    expense_category: Literal["事務用品費", "宿泊費", "資格精算費", "その他経費"] = Field(..., description="経費区分")
    amount: int = Field(..., ge=0, description="金額（円）")
    business_purpose: str = Field(..., min_length=1, description="業務目的")

    _validate_purchase_date = field_validator("purchase_date", mode="before")(classmethod(_cls_validate_date_format))


class ExpenseReportInput(BaseModel):
    """経費精算申請書生成ツール（generate_expense_report）の入力パラメータ"""
    items: List[ExpenseItem] = Field(..., min_length=1, description="経費明細リスト")


class TransportItem(BaseModel):
    """移動明細の1件"""
    travel_date: str = Field(..., description="移動日（YYYY-MM-DD）")
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(..., description="交通手段")
    fare: int = Field(..., ge=0, description="費用（円）")
    business_purpose: str = Field(..., min_length=1, description="業務目的")

    _validate_travel_date = field_validator("travel_date", mode="before")(classmethod(_cls_validate_date_format))


class TransportReportInput(BaseModel):
    """交通費精算申請書生成ツール（generate_transport_report）の入力パラメータ"""
    items: List[TransportItem] = Field(..., min_length=1, description="移動明細リスト")


# ============ 出力生成モデル ============

class TransportCalculatorOutput(BaseModel):
    """交通費計算ツールの出力構造"""
    success: bool = Field(..., description="計算成否")
    fare: Optional[int] = Field(None, ge=0, description="交通費金額（円）。成功時のみ設定")
    error_message: Optional[str] = Field(None, description="エラーメッセージ。失敗時のみ設定")


class ReportOutput(BaseModel):
    """申請書生成ツールの出力構造"""
    success: bool = Field(..., description="生成成否")
    file_path: Optional[str] = Field(None, description="生成ファイルパス。成功時のみ設定")
    error_message: Optional[str] = Field(None, description="エラーメッセージ。失敗時のみ設定")
