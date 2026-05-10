"""データモデルの定義

業務ドメインに応じたPydanticモデルを定義する。
各モデルはツール入力、エージェント状態、マスタデータの型安全性を保証する。
"""
from typing import Literal
from pydantic import BaseModel, Field, field_validator


# ============ 共通バリデーター ============

def validate_station_name(v: str) -> str:
    """駅名・バス停名等の接尾語を除去して正規化する（BRL-08）"""
    suffixes = ["駅", "バス停", "空港"]
    for suffix in suffixes:
        if v.endswith(suffix):
            return v[:-len(suffix)]
    return v


def validate_transport_type(v: str) -> str:
    """交通手段の表記ゆれを正規化する（BRL-03）"""
    mapping = {
        "train": "電車", "電鉄": "電車", "鉄道": "電車",
        "bus": "バス",
        "taxi": "タクシー", "cab": "タクシー",
        "airplane": "飛行機", "plane": "飛行機", "flight": "飛行機", "航空": "飛行機",
    }
    return mapping.get(v, v)


def validate_expense_category(v: str) -> str:
    """経費区分の表記ゆれを正規化する（BRL-12）"""
    mapping = {
        "事務用品": "事務用品費", "文具": "事務用品費",
        "宿泊": "宿泊費", "ホテル": "宿泊費",
        "資格": "資格精算費", "資格取得": "資格精算費",
        "その他": "その他経費",
    }
    return mapping.get(v, v)


def validate_date_format(v: str) -> str:
    """日付文字列のYYYY-MM-DD形式を検証する"""
    from datetime import datetime
    try:
        datetime.strptime(v, "%Y-%m-%d")
        return v
    except (ValueError, TypeError):
        raise ValueError(f"日付の形式が正しくありません。YYYY-MM-DD形式で入力してください: {v}")


# ============ マスタデータモデル ============

class TrainFareRecord(BaseModel):
    """train_fares.jsonの1レコードの型保証モデル"""
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    fare: float = Field(..., ge=0, description="運賃（円）")


class FixedFareRecord(BaseModel):
    """fixed_fares.jsonの固定運賃データの型保証モデル"""
    transport_type: Literal["バス", "タクシー", "飛行機"] = Field(..., description="交通手段")
    fare: float = Field(..., ge=0, description="固定運賃（円）")


# ============ ツール入力モデル ============

class TransportCalculatorInput(BaseModel):
    """TOOL-001（calculate_transport_fare）の入力バリデーションモデル"""
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(..., description="交通手段")
    travel_date: str = Field(..., description="移動日（YYYY-MM-DD形式）")

    @field_validator("departure", mode="before")
    @classmethod
    def _validate_departure(cls, v: str) -> str:
        return validate_station_name(v)

    @field_validator("destination", mode="before")
    @classmethod
    def _validate_destination(cls, v: str) -> str:
        return validate_station_name(v)

    @field_validator("transport_type", mode="before")
    @classmethod
    def _validate_transport_type(cls, v: str) -> str:
        return validate_transport_type(v)

    @field_validator("travel_date", mode="before")
    @classmethod
    def _validate_travel_date(cls, v: str) -> str:
        return validate_date_format(v)


class TransportItem(BaseModel):
    """交通費精算申請書の1移動明細"""
    travel_date: str = Field(..., description="移動日（YYYY-MM-DD形式）")
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(..., description="交通手段")
    fare: float = Field(..., ge=0, description="交通費（円）")
    purpose: str = Field(..., min_length=1, description="業務目的")

    @field_validator("travel_date", mode="before")
    @classmethod
    def _validate_travel_date(cls, v: str) -> str:
        return validate_date_format(v)

    @field_validator("departure", mode="before")
    @classmethod
    def _validate_departure(cls, v: str) -> str:
        return validate_station_name(v)

    @field_validator("destination", mode="before")
    @classmethod
    def _validate_destination(cls, v: str) -> str:
        return validate_station_name(v)

    @field_validator("transport_type", mode="before")
    @classmethod
    def _validate_transport_type(cls, v: str) -> str:
        return validate_transport_type(v)


class TransportFormInput(BaseModel):
    """TOOL-002（generate_transport_form）の入力バリデーションモデル"""
    applicant_name: str = Field(..., min_length=1, description="申請者名")
    application_date: str = Field(..., description="申請日（YYYY-MM-DD形式）")
    items: list[TransportItem] = Field(..., min_length=1, description="移動明細リスト")

    @field_validator("application_date", mode="before")
    @classmethod
    def _validate_application_date(cls, v: str) -> str:
        return validate_date_format(v)


class ExpenseItem(BaseModel):
    """経費精算申請書の1経費明細"""
    purchase_date: str = Field(..., description="購入日（YYYY-MM-DD形式）")
    item_name: str = Field(..., min_length=1, description="品目")
    amount: float = Field(..., ge=0, description="金額（円）")
    expense_category: Literal["事務用品費", "宿泊費", "資格精算費", "その他経費"] = Field(..., description="経費区分")
    purpose: str = Field(..., min_length=1, description="業務目的")

    @field_validator("purchase_date", mode="before")
    @classmethod
    def _validate_purchase_date(cls, v: str) -> str:
        return validate_date_format(v)

    @field_validator("expense_category", mode="before")
    @classmethod
    def _validate_expense_category(cls, v: str) -> str:
        return validate_expense_category(v)


class ExpenseFormInput(BaseModel):
    """TOOL-002（generate_expense_form）の入力バリデーションモデル"""
    applicant_name: str = Field(..., min_length=1, description="申請者名")
    application_date: str = Field(..., description="申請日（YYYY-MM-DD形式）")
    items: list[ExpenseItem] = Field(..., min_length=1, description="経費明細リスト")

    @field_validator("application_date", mode="before")
    @classmethod
    def _validate_application_date(cls, v: str) -> str:
        return validate_date_format(v)


# ============ ツール出力モデル ============

class TransportCalculatorOutput(BaseModel):
    """TOOL-001（calculate_transport_fare）の出力型保証モデル"""
    success: bool = Field(..., description="処理成功フラグ")
    fare: float = Field(0.0, ge=0, description="交通費（円）")
    calculation_basis: str = Field("", description="計算根拠")
    not_found: bool = Field(False, description="経路未登録フラグ")
    error_message: str = Field("", description="エラーメッセージ")


class TransportFormOutput(BaseModel):
    """TOOL-002（generate_transport_form）の出力型保証モデル"""
    success: bool = Field(..., description="処理成功フラグ")
    file_path: str = Field("", description="生成ファイルパス")
    error_message: str = Field("", description="エラーメッセージ")


class ExpenseFormOutput(BaseModel):
    """TOOL-002（generate_expense_form）の出力型保証モデル"""
    success: bool = Field(..., description="処理成功フラグ")
    file_path: str = Field("", description="生成ファイルパス")
    error_message: str = Field("", description="エラーメッセージ")
