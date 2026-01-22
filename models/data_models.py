"""データモデルの定義"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class RouteData:
    """一区間の経路情報"""
    departure: str          # 出発地
    destination: str        # 目的地
    date: datetime          # 移動日
    transport_type: str     # 交通手段（train/bus/taxi/airplane）
    cost: float            # 計算された費用
    notes: Optional[str] = None   # 備考
    
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


@dataclass
class ExpenseReport:
    """交通費申請書"""
    user_id: str
    report_date: datetime
    routes: List[RouteData]
    total_cost: float
    
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
