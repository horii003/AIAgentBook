"""データモデルの定義"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator


# 共通バリデーター
def validate_date_string(v: str) -> str:
    """日付文字列のバリデーション（YYYY-MM-DD形式）"""
    try:
        datetime.strptime(v, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"日付はYYYY-MM-DD形式である必要があります: {v}")
    return v


def normalize_transport_type(v: str) -> str:
    """交通手段を英語に正規化"""
    mapping = {"電車": "train", "バス": "bus", "タクシー": "taxi", "飛行機": "airplane"}
    return mapping.get(v, v.lower())


class TrainFareRoute(BaseModel):
    """電車運賃の経路データ"""
    departure: str = Field(..., description="出発地")
    destination: str = Field(..., description="目的地")
    fare: float = Field(..., description="運賃", gt=0)


class FareData(BaseModel):
    """運賃データ全体"""
    train_fares: List[TrainFareRoute] = Field(..., description="電車運賃リスト")
    fixed_fares: dict = Field(..., description="固定運賃（bus/taxi/airplane）")
    
    @field_validator("fixed_fares")
    @classmethod
    def validate_fixed_fares(cls, v: dict) -> dict:
        """固定運賃に必須の交通手段が含まれているか確認"""
        required_types = ["bus", "taxi", "airplane"]
        missing = [t for t in required_types if t not in v]
        if missing:
            raise ValueError(f"固定運賃データに必須の交通手段が不足しています: {', '.join(missing)}")
        return v


class RouteInput(BaseModel):
    """ツール入力用の経路データ（dateが文字列の場合に対応）"""
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    date: str = Field(..., description="日付（YYYY-MM-DD形式）")
    transport_type: Literal["train", "bus", "taxi", "airplane", "電車", "バス", "タクシー", "飛行機"] = Field(..., description="交通手段")
    cost: float = Field(..., ge=0, description="費用")
    notes: Optional[str] = Field(None, description="備考")
    
    _validate_date = field_validator("date")(validate_date_string)
    _normalize_transport = field_validator("transport_type")(normalize_transport_type)


class InvocationState(BaseModel):
    """エージェント呼び出し時の状態データ
    
    AWS Strandsのinvocation_stateから渡されるデータの型安全性を保証する。
    """
    applicant_name: str = Field(..., min_length=1, description="申請者名")
    application_date: str = Field(..., description="申請日（YYYY-MM-DD形式）")
    session_id: Optional[str] = Field(None, description="セッションID")
    
    _validate_date = field_validator("application_date")(validate_date_string)


class FareCalculationInput(BaseModel):
    """運賃計算ツールの入力データ"""
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    transport_type: Literal["train", "bus", "taxi", "airplane", "電車", "バス", "タクシー", "飛行機"] = Field(..., description="交通手段")
    date: str = Field(..., description="移動日（YYYY-MM-DD形式）")
    
    _validate_date = field_validator("date")(validate_date_string)
    _normalize_transport = field_validator("transport_type")(normalize_transport_type)


class ReceiptExpenseInput(BaseModel):
    """経費精算申請の入力データ"""
    store_name: str = Field(..., min_length=1, description="店舗名")
    amount: float = Field(..., gt=0, description="金額（円）")
    date: str = Field(..., description="購入日（YYYY-MM-DD形式）")
    items: List[str] = Field(..., min_length=1, description="品目リスト")
    expense_category: str = Field(..., min_length=1, description="経費区分")
    
    _validate_date = field_validator("date")(validate_date_string)

