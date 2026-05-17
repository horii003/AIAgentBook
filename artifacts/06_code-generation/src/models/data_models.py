"""データモデルの定義

業務ドメインに応じたPydanticモデルを定義する。
各モデルはツール入力、マスタデータ、出力生成の型安全性を保証する。
"""

from typing import Literal, Optional

from dateutil import parser as date_parser
from pydantic import BaseModel, Field, field_validator


# ============ 共通バリデーター ============


def validate_station_name(v: str) -> str:
    """駅名の正規化バリデーター

    末尾「駅」を除去し、空文字をチェックする。
    """
    if not v or not v.strip():
        raise ValueError("駅名を入力してください。")
    return v.strip().removesuffix("駅").strip()


def normalize_transport_type(v: str) -> str:
    """交通手段の正規化バリデーター

    英語表記を日本語に変換する。
    """
    mapping = {
        "train": "電車",
        "電車": "電車",
        "bus": "バス",
        "バス": "バス",
        "taxi": "タクシー",
        "タクシー": "タクシー",
        "airplane": "飛行機",
        "plane": "飛行機",
        "飛行機": "飛行機",
    }
    normalized = mapping.get(v.strip().lower() if v else "")
    if normalized is None:
        # 日本語入力の場合はそのまま検索
        normalized = mapping.get(v.strip() if v else "")
    if normalized is None:
        raise ValueError(
            "交通手段は電車・バス・タクシー・飛行機のいずれかを指定してください。"
        )
    return normalized


def validate_date_format(v: str) -> str:
    """日付形式の正規化バリデーター

    柔軟な日付文字列をYYYY-MM-DD形式に正規化する。
    """
    if not v or not v.strip():
        raise ValueError("日付の形式が正しくありません（YYYY-MM-DD 形式で入力してください）。")
    try:
        parsed = date_parser.parse(v.strip())
        return parsed.strftime("%Y-%m-%d")
    except (ValueError, TypeError) as e:
        raise ValueError(
            "日付の形式が正しくありません（YYYY-MM-DD 形式で入力してください）。"
        ) from e


# ============ マスタデータモデル ============


class TrainRouteRecord(BaseModel):
    """電車経路・運賃データの1レコード"""

    departure: str = Field(..., min_length=1, description="出発駅")
    destination: str = Field(..., min_length=1, description="到着駅")
    fare: int = Field(..., gt=0, description="運賃（円）")


# ============ ツール入力モデル ============


class TransportCalculatorInput(BaseModel):
    """交通費計算ツールの入力パラメータ検証"""

    departure: str = Field(..., min_length=1, description="出発地（正規化済み駅名）")
    destination: str = Field(..., min_length=1, description="目的地（正規化済み駅名）")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(
        ..., description="交通手段"
    )
    travel_date: str = Field(..., description="移動日（YYYY-MM-DD）")

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
        return normalize_transport_type(v)

    @field_validator("travel_date", mode="before")
    @classmethod
    def _validate_travel_date(cls, v: str) -> str:
        return validate_date_format(v)


class TransportCalculatorOutput(BaseModel):
    """交通費計算ツールの出力構造"""

    success: bool = Field(..., description="計算成否")
    fare: Optional[int] = Field(None, ge=0, description="交通費金額（円）")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")


# ============ 出力生成モデル ============


class ExpenseItem(BaseModel):
    """経費明細の1件"""

    purchase_date: str = Field(..., description="購入日（YYYY-MM-DD）")
    store_name: str = Field(..., min_length=1, description="店舗名")
    item_name: str = Field(..., min_length=1, description="品目")
    expense_category: Literal["事務用品費", "宿泊費", "資格精算費", "その他経費"] = Field(
        ..., description="経費区分"
    )
    amount: int = Field(..., ge=0, description="金額（円）")
    business_purpose: str = Field(..., min_length=1, description="業務目的")

    @field_validator("purchase_date", mode="before")
    @classmethod
    def _validate_purchase_date(cls, v: str) -> str:
        return validate_date_format(v)


class ExpenseReportInput(BaseModel):
    """経費精算申請書生成ツールの入力パラメータ検証"""

    items: list[ExpenseItem] = Field(..., min_length=1, description="経費明細リスト")


class TransportItem(BaseModel):
    """移動明細の1件"""

    travel_date: str = Field(..., description="移動日（YYYY-MM-DD）")
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(
        ..., description="交通手段"
    )
    fare: int = Field(..., ge=0, description="費用（円）")
    business_purpose: str = Field(..., min_length=1, description="業務目的")

    @field_validator("travel_date", mode="before")
    @classmethod
    def _validate_travel_date(cls, v: str) -> str:
        return validate_date_format(v)


class TransportReportInput(BaseModel):
    """交通費精算申請書生成ツールの入力パラメータ検証"""

    items: list[TransportItem] = Field(..., min_length=1, description="移動明細リスト")


class ReportOutput(BaseModel):
    """申請書生成ツールの出力構造"""

    success: bool = Field(..., description="生成成否")
    file_path: Optional[str] = Field(None, description="生成ファイルパス")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")
