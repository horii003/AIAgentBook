# スケルトン: データモデル定義 (models/data_models.py)

## 概要

Pydanticモデルを用いてアプリケーション全体の型安全性を保証するデータモデル定義。
業務ドメインに応じてモデルを追加・カスタマイズする。

## ファイル配置

`models/data_models.py`

---

## Pydanticモデル共通ルール

### モデルカテゴリと用途

| カテゴリ | 用途 | 定義元 | 利用先 |
|:---|:---|:---|:---|
| マスタデータモデル | `data/`配下のJSONファイルの型保証 | JSONデータ構造に対応 | `tools/{domain}_tools.py` |
| ツール入力モデル | ツール関数の入力パラメータの型保証 | ツール関数の引数に対応 | `tools/{domain}_tools.py` |
| エージェント状態モデル | `invocation_state`の型保証 | エージェント間の状態受け渡し | `agents/`, `tools/` |
| 出力生成モデル | 出力ファイル生成時のデータ型保証 | 出力内容の構造に対応 | `tools/output_generator.py` |

### Field定義パターン

| パターン | 用途 | 例 |
|:---|:---|:---|
| `Field(..., description="説明")` | 必須フィールド | `name: str = Field(..., description="名称")` |
| `Field(None, description="説明")` | 任意フィールド（デフォルトNone） | `notes: Optional[str] = Field(None, description="備考")` |
| `Field(..., min_length=1)` | 空文字禁止 | `name: str = Field(..., min_length=1, description="名称")` |
| `Field(..., gt=0)` | 正の数値のみ | `amount: float = Field(..., gt=0, description="金額")` |
| `Field(..., ge=0)` | 0以上の数値 | `cost: float = Field(..., ge=0, description="費用")` |
| `Literal[...]` | 許可値の列挙 | `category: Literal["A", "B", "C"]` |

### バリデーターの適用パターン

| パターン | 用途 | 例 |
|:---|:---|:---|
| 共通バリデーター関数の適用 | 複数モデルで共有するバリデーション | `_validate_xxx = field_validator("field_name", mode="before")(classmethod(validate_xxx))` |
| クラスメソッドバリデーター | モデル固有のバリデーション | `@field_validator("items")` + `@classmethod` |

> **ラムダラッパーの禁止**: `classmethod(lambda cls, v: validate_xxx(v))` のように既存の共通バリデーター関数を単純にラムダで包むのは冗長。`classmethod(validate_xxx)` として直接渡すこと。

### バリデーション実行タイミング（R9.3準拠）

| タイミング | 実行箇所 | 例 |
|:---|:---|:---|
| ツール関数の入口 | `tools/{domain}_tools.py` | `input_data = SearchInput(**raw_data)` |
| invocation_state受取時 | `agents/orchestrator_agent.py` | `InvocationState(user_name=..., ...)` |
| invocation_stateの再バリデーション | `tools/output_generator.py` | `InvocationState(**tool_context.invocation_state)` |
| マスタデータ読み込み時 | `tools/{domain}_tools.py` | `MasterData(**json_data)` |

---

## スケルトンコード

```python
"""データモデルの定義

業務ドメインに応じたPydanticモデルを定義する。
各モデルはツール入力、エージェント状態、マスタデータの型安全性を保証する。
"""
from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator


# ============ 共通バリデーター ============
# 複数モデルで共有するバリデーター関数を定義し、field_validatorで各モデルに適用する
#
# def validate_xxx(v: str) -> str:
#     """共通バリデーター"""
#     ...
#     return v

# TODO: 業務要件に応じて共通バリデーター関数を定義


# ============ エージェント状態モデル ============

class InvocationState(BaseModel):
    """エージェント呼び出し時の状態データ"""
    session_id: Optional[str] = Field(None, description="セッションID")

    # TODO: 業務要件に応じてフィールド・バリデーターを追加


# ============ マスタデータモデル ============

# TODO: data/配下のJSONファイル構造に対応するモデルを定義


# ============ ツール入力モデル ============

# TODO: ツール関数の入力パラメータに対応するモデルを定義


# ============ 出力生成モデル ============

# TODO: 出力ファイル生成時のデータ構造に対応するモデルを定義
```

## カスタマイズガイド

1. **共通バリデーター**: 業務ドメインで頻繁に使用するバリデーション（カテゴリ正規化、コード検証等）を追加する
2. **マスタデータモデル**: `data/` 配下のJSONファイル構造に対応するモデルを定義する
3. **ツール入力モデル**: 各ツール関数の入力パラメータに対応するモデルを定義する
4. **エージェント状態モデル（InvocationState）**: オーケストレーターと専門エージェント間で共有する状態情報のフィールドを定義する
5. **出力生成モデル**: 出力ファイル生成時のデータ構造に対応するモデルを定義する
6. **【禁止】未使用モデルの定義**: 定義したモデルは対応するツール関数内で実際に使用すること。ツール出力モデル（`XxxOutput`）はツール戻り値の構築に、マスタデータモデルはデータ読み込み時に使用する。使用されないモデルはデッドコードとして削除する
