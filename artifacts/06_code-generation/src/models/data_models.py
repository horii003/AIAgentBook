"""データモデルの定義

業務ドメインに応じたPydanticモデルを定義する。
各モデルはツール入力、エージェント状態、マスタデータの型安全性を保証する。
"""
import re
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator


# ============ 共通バリデーター ============

def validate_date(v: str) -> str:
    """日付文字列を YYYY-MM-DD 形式に正規化する。

    Args:
        v: 日付文字列

    Returns:
        YYYY-MM-DD形式の日付文字列

    Raises:
        ValueError: パース不可能な日付形式の場合
    """
    if not v or not isinstance(v, str):
        raise ValueError("日付が入力されていません")

    v = v.strip()

    # YYYY-MM-DD形式
    if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
        datetime.strptime(v, "%Y-%m-%d")
        return v

    # YYYY/MM/DD形式
    if re.match(r"^\d{4}/\d{2}/\d{2}$", v):
        parsed = datetime.strptime(v, "%Y/%m/%d")
        return parsed.strftime("%Y-%m-%d")

    # YYYY年MM月DD日形式
    match = re.match(r"^(\d{4})年(\d{1,2})月(\d{1,2})日$", v)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        parsed = datetime(year, month, day)
        return parsed.strftime("%Y-%m-%d")

    raise ValueError(f"日付形式が不正です: {v}（YYYY-MM-DD, YYYY/MM/DD, YYYY年MM月DD日 のいずれかで入力してください）")


def validate_amount(v) -> int:
    """金額を整数に正規化する。

    Args:
        v: 金額（str, int, float）

    Returns:
        0以上の整数

    Raises:
        ValueError: 変換不可能または負の値の場合
    """
    if isinstance(v, int):
        if v < 0:
            raise ValueError(f"金額は0以上である必要があります: {v}")
        return v

    if isinstance(v, float):
        if v < 0:
            raise ValueError(f"金額は0以上である必要があります: {v}")
        return int(v)

    if isinstance(v, str):
        v = v.strip().replace(",", "").replace("円", "")
        try:
            result = int(v)
        except ValueError:
            raise ValueError(f"金額を数値に変換できません: {v}")
        if result < 0:
            raise ValueError(f"金額は0以上である必要があります: {result}")
        return result

    raise ValueError(f"金額の型が不正です: {type(v)}")


def normalize_transport_type(v: str) -> str:
    """交通手段の表記を正規化する。

    Args:
        v: 交通手段文字列

    Returns:
        正規化された交通手段文字列
    """
    if not isinstance(v, str):
        return v

    v = v.strip()

    mapping = {
        "鉄道": "電車",
        "JR": "電車",
        "地下鉄": "電車",
        "路線バス": "バス",
        "航空機": "飛行機",
    }

    return mapping.get(v, v)


def normalize_expense_category(v: str) -> str:
    """経費カテゴリの表記を正規化する。

    Args:
        v: 経費カテゴリ文字列

    Returns:
        正規化された経費カテゴリ文字列
    """
    if not isinstance(v, str):
        return v

    v = v.strip()

    mapping = {
        "事務用品": "事務用品費",
        "宿泊": "宿泊費",
        "ホテル": "宿泊費",
        "資格": "資格精算費",
        "試験": "資格精算費",
        "その他": "その他経費",
    }

    return mapping.get(v, v)


# ============ エージェント状態モデル ============

class InvocationState(BaseModel):
    """オーケストレーターから子エージェントへ渡す共有状態

    invocation_state はLLMのコンテキストウィンドウを消費せず、
    ツール関数内でのみ参照できる（@tool(context=True) + tool_context.invocation_state）。
    """
    applicant_name: str = Field(..., min_length=1, description="申請者名")
    application_date: str = Field(..., description="申請日（YYYY-MM-DD）")
    session_id: str = Field(..., min_length=1, description="セッションID")

    @field_validator("application_date", mode="before")
    @classmethod
    def _validate_application_date(cls, v: str) -> str:
        return validate_date(v)


# ============ マスタデータモデル ============

class RouteData(BaseModel):
    """路線運賃マスタデータモデル"""
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    fare: int = Field(..., ge=0, description="運賃（円）")


# ============ ツール入力モデル ============

class TransportCalculatorInput(BaseModel):
    """交通費計算ツールの入力モデル"""
    departure: str = Field(..., min_length=1, description="出発地")
    destination: str = Field(..., min_length=1, description="目的地")
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"] = Field(..., description="交通手段")
    travel_date: str = Field(..., description="移動日（YYYY-MM-DD）")

    @field_validator("transport_type", mode="before")
    @classmethod
    def _normalize_transport_type(cls, v: str) -> str:
        return normalize_transport_type(v)

    @field_validator("travel_date", mode="before")
    @classmethod
    def _validate_travel_date(cls, v: str) -> str:
        return validate_date(v)


class TransportationExpenseFormInput(BaseModel):
    """交通費精算書出力ツールの入力モデル"""
    items: list = Field(..., min_length=1, description="区間情報リスト")

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list) -> list:
        """items内の各要素のバリデーションを実行する。"""
        validated_items = []
        for i, item in enumerate(v):
            item = dict(item) if not isinstance(item, dict) else item.copy()
            if "travel_date" not in item:
                raise ValueError(f"items[{i}]: travel_date は必須です")
            if "amount" not in item:
                raise ValueError(f"items[{i}]: amount は必須です")
            item["travel_date"] = validate_date(item["travel_date"])
            item["amount"] = validate_amount(item["amount"])
            validated_items.append(item)
        return validated_items


class GeneralExpenseFormInput(BaseModel):
    """一般経費精算書出力ツールの入力モデル"""
    items: list = Field(..., min_length=1, description="経費明細リスト")

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list) -> list:
        """items内の各要素のバリデーションを実行する。"""
        validated_items = []
        for i, item in enumerate(v):
            item = dict(item) if not isinstance(item, dict) else item.copy()
            if "purchase_date" not in item:
                raise ValueError(f"items[{i}]: purchase_date は必須です")
            if "amount" not in item:
                raise ValueError(f"items[{i}]: amount は必須です")
            item["purchase_date"] = validate_date(item["purchase_date"])
            item["expense_category"] = normalize_expense_category(item.get("expense_category", ""))
            item["amount"] = validate_amount(item["amount"])
            validated_items.append(item)
        return validated_items


# ============ 出力生成モデル ============

class TransportCalculatorOutput(BaseModel):
    """交通費計算ツールの出力モデル"""
    success: bool = Field(..., description="処理成功フラグ")
    fare: Optional[int] = Field(None, ge=0, description="運賃（円）")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")
    is_expired: Optional[bool] = Field(None, description="申請期限超過フラグ")


class FormGeneratorOutput(BaseModel):
    """精算書出力ツールの出力モデル"""
    success: bool = Field(..., description="処理成功フラグ")
    file_path: Optional[str] = Field(None, description="出力ファイルパス")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")
