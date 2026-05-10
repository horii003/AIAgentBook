# スケルトン: ドメイン固有ツール (tools/{domain}_tools.py)

## 概要

専門エージェントが利用するドメイン固有のツール関数を定義するテンプレート。
データ検索、計算、変換等の処理をツールとして提供する。

## ファイル配置

`tools/{domain}_tools.py`（例: `tools/search_tools.py`, `tools/calculation_tools.py`）

## スケルトンコード

```python
"""
{ドメイン}関連のツール

{ドメインの説明}に必要なツール関数を提供する。
"""
import json
import os
from typing import Tuple
from strands import tool
from pydantic import ValidationError
from models.data_models import {MasterData}, {ToolInput}
from handlers.error_handler import ErrorHandler


# ============ データ読み込み関数 ============

# TODO: data/配下のJSONファイルに対応する読み込み関数を定義
# - 戻り値: Tuple[bool, dict | str]（成功フラグ, データまたはエラーメッセージ）
# - Pydanticモデルでバリデーション
# - エラー時: handle_data_load_error()でエラーメッセージを生成


# ============ ドメイン固有ツール ============

@tool
def {tool_function_name}(
    param_a: str,
    param_b: str,
    param_c: str
) -> dict:
    """
    {ツールの説明}

    Args:
        param_a: {パラメータAの説明}
        param_b: {パラメータBの説明}
        param_c: {パラメータCの説明}

    Returns:
        dict: {
            "success": bool,         # 成功フラグ
            "result": any,           # 処理結果（エラー時はNone）
            "message": str           # 結果メッセージ（エラー時はエラーメッセージ）
        }
    """
    # TODO: 詳細設計書に従い実装
    # - ツール呼び出しログ出力
    # - 入力パラメータのバリデーション（Pydanticモデル）
    # - マスタデータの読み込み（必要な場合）
    # - ドメイン固有の処理（検索、計算、変換等）
    # - 結果辞書の返却
    # - エラーハンドリング（ValidationError、その他のException）
    pass


# TODO: 業務要件に応じてツール関数を追加


# ============ 出力生成ツール ============
# invocation_stateからユーザー情報を参照するため @tool(context=True) を使用する
# ファイル配置: tools/output_generator.py（別ファイルに分離してもよい）

# @tool(context=True)
# def {output_generator_name}(..., tool_context: ToolContext) -> dict:
#     """処理結果を出力ファイルとして生成する"""
#     # - tool_context.invocation_stateからユーザー情報を取得
#     # - 出力ファイル生成（Excel、PDF、CSV等）
#     # - HumanApprovalHookの対象ツールとして登録
#     pass
```

## ツール設計パターン

### 戻り値の標準構造

全ツール関数は以下の辞書構造で結果を返却する：

```python
# 成功時
{
    "success": True,
    "result": <処理結果>,       # データ型はツールごとに異なる
    "message": "処理が完了しました"
}

# エラー時
{
    "success": False,
    "result": None,
    "message": "エラーメッセージ（ユーザー向け）"
}
```

### ツール関数の分類

| デコレータ | 用途 | 説明 |
|:---|:---|:---|
| `@tool` | `invocation_state`を参照しないツール | データ検索、計算、変換等 |
| `@tool(context=True)` | `invocation_state`を参照するツール | 出力生成等、ユーザーコンテキストが必要な処理 |

業務要件に応じてStrandsの組み込みツール（`strands_tools`）も利用可能。
AWS Strands Toolsには以下の組み込みツールが利用可能。業務要件に応じて選択する：
`strands_tools.image_reader` - 画像読み取り

## カスタマイズガイド

1. **マスタデータ読み込み**: `data/` 配下のJSONファイルに対応する読み込み関数を定義する
2. **ツール関数の追加**: 業務要件に応じて `@tool` デコレートされた関数を追加する
3. **入力バリデーション**: 各ツール関数の入力パラメータに対応するPydanticモデルを `models/data_models.py` に定義する
4. **エラーハンドリング**: ValidationError → ドメイン固有エラー → 予期しないエラーの順でキャッチする。同一処理を実行する複数の `except` 節は統合すること（R9.1参照）
5. **出力生成ツール**: `@tool(context=True)` を使用し、`invocation_state` からユーザー情報を取得する。`HumanApprovalHook` の対象ツールとして登録する
6. **DRY原則**: 複数のツール関数で同じ処理フロー（invocation_state取得 → バリデーション → ファイル存在確認 → 生成 → 保存）が繰り返される場合は、内部ヘルパー関数に抽出して重複を排除すること（R9.12.1参照）
7. **ErrorHandlerの呼び出し方**: `ErrorHandler` はインスタンス化せず、`ErrorHandler.handle_xxx()` と静的メソッドとして直接呼び出すこと（R9.1参照）
