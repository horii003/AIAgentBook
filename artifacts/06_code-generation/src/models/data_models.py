"""データモデルの定義

業務ドメインに応じたPydanticモデルを定義する。
共通バリデーター関数とエージェント状態モデルを提供する。
各ツール固有のモデルはそれぞれのツールファイルで定義する。
"""
from typing import Optional
from dateutil import parser
from pydantic import BaseModel, Field, field_validator


# ============ 共通バリデーター ============

def validate_date_format(cls, v: str) -> str:
    """日付文字列がYYYY-MM-DD形式の有効な日付であることを検証する。

    Args:
        cls: クラス（field_validatorのclassmethodとして使用）
        v: 検証する日付文字列

    Returns:
        検証済みの日付文字列

    Raises:
        ValueError: 日付形式が不正な場合
    """
    try:
        parsed = parser.parse(v)
        # YYYY-MM-DD形式であることを確認
        if parsed.strftime("%Y-%m-%d") != v:
            raise ValueError(f"日付はYYYY-MM-DD形式で入力してください: {v}")
    except (ValueError, OverflowError) as e:
        raise ValueError(f"日付はYYYY-MM-DD形式で入力してください: {v}") from e
    return v


def normalize_transport_type(cls, v: str) -> str:
    """交通手段の表記を正規化する（英語表記・略称を日本語正規表記に変換）。

    Args:
        cls: クラス（field_validatorのclassmethodとして使用）
        v: 正規化する交通手段文字列

    Returns:
        正規化された交通手段文字列
    """
    mapping = {
        "train": "電車",
        "bus": "バス",
        "taxi": "タクシー",
        "airplane": "飛行機",
        "plane": "飛行機",
    }
    return mapping.get(v.lower() if isinstance(v, str) else v, v)


def normalize_expense_category(cls, v: str) -> str:
    """経費区分の表記を正規化する（英語表記・略称を日本語正規表記に変換）。

    Args:
        cls: クラス（field_validatorのclassmethodとして使用）
        v: 正規化する経費区分文字列

    Returns:
        正規化された経費区分文字列
    """
    mapping = {
        "office_supplies": "事務用品費",
        "accommodation": "宿泊費",
        "qualification": "資格精算費",
        "other": "その他経費",
        "その他": "その他経費",
    }
    return mapping.get(v, v)


# ============ エージェント状態モデル ============

class InvocationState(BaseModel):
    """オーケストレーターから子エージェントへ渡す共有状態。

    invocation_stateはLLMのコンテキストウィンドウを消費せず、
    ツール関数内でのみ参照できる（@tool(context=True) + tool_context.invocation_state）。
    """

    user_name: str = Field(..., description="申請者名")
    request_date: str = Field(..., description="申請日（YYYY-MM-DD）")
    session_id: str = Field(..., description="セッションID（子エージェントのファクトリで消費）")

    _validate_request_date = field_validator("request_date", mode="before")(
        classmethod(validate_date_format)
    )
