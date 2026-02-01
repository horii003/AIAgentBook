"""データモデルの定義"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class RouteData(BaseModel):
    """一区間の経路情報"""
    departure: str = Field(..., description="出発地", min_length=1)
    destination: str = Field(..., description="目的地", min_length=1)
    date: datetime = Field(..., description="移動日")
    transport_type: Literal["train", "bus", "taxi", "airplane"] = Field(
        ..., description="交通手段（train/bus/taxi/airplane）"
    )
    cost: float = Field(..., description="計算された費用", ge=0)
    notes: Optional[str] = Field(None, description="備考")
    
    @field_validator("cost")
    @classmethod
    def validate_cost(cls, v: float) -> float:
        """費用が妥当な範囲内かチェック"""
        if v < 0:
            raise ValueError("費用は0以上である必要があります")
        if v > 1000000:
            raise ValueError("費用が大きすぎます（100万円以下）")
        return v
    
    def to_dict(self) -> dict:
        """辞書形式に変換"""
        return {
            "departure": self.departure,
            "destination": self.destination,
            "date": self.date.strftime("%Y-%m-%d"),
            "transport_type": self.transport_type,
            "cost": self.cost,
            "notes": self.notes
        }


class ExpenseReport(BaseModel):
    """交通費申請書"""
    user_id: str = Field(..., description="申請者ID", min_length=1)
    report_date: datetime = Field(..., description="申請日")
    routes: List[RouteData] = Field(..., description="経路リスト", min_length=1)
    total_cost: float = Field(..., description="合計経費", ge=0)
    
    @field_validator("routes")
    @classmethod
    def validate_routes(cls, v: List[RouteData]) -> List[RouteData]:
        """経路リストが空でないことを確認"""
        if not v:
            raise ValueError("経路リストは空にできません")
        return v
    
    def to_dict(self) -> dict:
        """辞書形式に変換（JSON出力用）"""
        return {
            "user_id": self.user_id,
            "report_date": self.report_date.strftime("%Y-%m-%d"),
            "routes": [route.to_dict() for route in self.routes],
            "total_cost": self.total_cost
        }
    
    def to_pdf_content(self) -> str:
        """PDF生成用のコンテンツを作成"""
        content = f"交通費申請書\n\n"
        content += f"申請者ID: {self.user_id}\n"
        content += f"申請日: {self.report_date.strftime('%Y年%m月%d日')}\n\n"
        content += "=" * 60 + "\n\n"
        content += "経路一覧:\n\n"
        
        for i, route in enumerate(self.routes, 1):
            content += f"{i}. {route.date.strftime('%Y年%m月%d日')}\n"
            content += f"   出発地: {route.departure}\n"
            content += f"   目的地: {route.destination}\n"
            content += f"   交通手段: {route.transport_type}\n"
            content += f"   費用: ¥{route.cost:,.0f}\n"
            if route.notes:
                content += f"   備考: {route.notes}\n"
            content += "\n"
        
        content += "=" * 60 + "\n"
        content += f"合計経費: ¥{self.total_cost:,.0f}\n"
        
        return content



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
            raise ValueError(f"固定運賃データに必須の交通手段が不足: {missing}")
        return v


class RouteInput(BaseModel):
    """ツール入力用の経路データ（dateが文字列の場合に対応）"""
    departure: str = Field(..., description="出発地", min_length=1)
    destination: str = Field(..., description="目的地", min_length=1)
    date: str = Field(..., description="日付（YYYY-MM-DD形式）")
    transport_type: Literal["train", "bus", "taxi", "airplane"] = Field(
        ..., description="交通手段"
    )
    cost: float = Field(..., description="費用", ge=0)
    notes: Optional[str] = Field(None, description="備考")
    
    @field_validator("date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """日付形式の検証"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"日付はYYYY-MM-DD形式である必要があります: {v}")
        return v


class InvocationState(BaseModel):
    """エージェント呼び出し時の状態データ
    
    AWS Strandsのinvocation_stateから渡されるデータの型安全性を保証する。
    """
    applicant_name: str = Field(..., description="申請者名", min_length=1)
    application_date: str = Field(..., description="申請日（YYYY-MM-DD形式）")
    session_id: Optional[str] = Field(None, description="セッションID")
    
    @field_validator("application_date")
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """日付形式の検証"""
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"日付はYYYY-MM-DD形式である必要があります: {v}")
        return v
