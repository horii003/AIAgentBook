# Design Document: Excel Generator Refactoring

## Overview

このドキュメントは、`tools/excel_generator.py`のリファクタリング設計を定義します。現在のモジュールには2つの独立した関数（`receipt_excel_generator`と`travel_excel_generator`）が存在し、以下の共通機能で大量のコード重複が発生しています：

- 申請者名の取得（invocation_stateから）
- タイムスタンプ付きファイル名の生成
- 出力ディレクトリの作成と管理
- Excelワークブックの作成と基本設定
- スタイル定義（フォント、色、配置）
- ファイル保存処理
- エラーハンドリングと戻り値の構造

このリファクタリングの目標は、共通機能を再利用可能なヘルパー関数に抽出し、コードの重複を削減しながら、既存のエージェント（`receipt_expense_agent`と`travel_agent`）との互換性を完全に維持することです。

### 設計原則

1. **後方互換性**: 既存のツールインターフェース（パラメータ、戻り値）を変更しない
2. **単一責任の原則**: 各ヘルパー関数は1つの明確な責任を持つ
3. **DRY原則**: 重複コードを排除し、共通ロジックを一箇所に集約
4. **テスト互換性**: 既存のテストコードが引き続き動作する

## Architecture

### 現在のアーキテクチャ

```
receipt_excel_generator()
├── 申請者名取得
├── 金額チェック
├── ファイル名生成
├── ディレクトリ作成
├── Excelワークブック作成
├── スタイル定義
├── データ入力（領収書用）
└── ファイル保存

travel_excel_generator()
├── 申請者名取得
├── データバリデーション
├── ファイル名生成
├── ディレクトリ作成
├── Excelワークブック作成
├── スタイル定義
├── データ入力（交通費用）
└── ファイル保存
```

### リファクタリング後のアーキテクチャ

```
共通ヘルパー関数層:
├── _get_applicant_name(tool_context) -> str
├── _generate_filename(prefix: str) -> str
├── _ensure_output_directory() -> Path
├── _create_workbook(title: str) -> tuple[Workbook, Worksheet]
├── _create_style_definitions() -> dict
├── _apply_header_style(cell, styles) -> None
├── _apply_title_style(cell, styles) -> None
└── _save_workbook(wb, file_path) -> bool

公開ツール関数層:
├── receipt_excel_generator(...)
│   ├── _get_applicant_name()を使用
│   ├── _generate_filename()を使用
│   ├── _ensure_output_directory()を使用
│   ├── _create_workbook()を使用
│   ├── _create_style_definitions()を使用
│   ├── 領収書固有のデータ入力ロジック
│   └── _save_workbook()を使用
│
└── travel_excel_generator(...)
    ├── _get_applicant_name()を使用
    ├── _generate_filename()を使用
    ├── _ensure_output_directory()を使用
    ├── _create_workbook()を使用
    ├── _create_style_definitions()を使用
    ├── 交通費固有のデータ入力ロジック
    └── _save_workbook()を使用
```

### 設計の利点

1. **保守性の向上**: 共通ロジックの変更が1箇所で済む
2. **テスト容易性**: ヘルパー関数を個別にテスト可能
3. **拡張性**: 新しいExcel生成機能を追加する際に共通関数を再利用可能
4. **可読性**: 各関数の責任が明確になり、コードが理解しやすくなる

## Components and Interfaces

### 1. 共通ヘルパー関数

#### 1.1 申請者名取得関数

```python
def _get_applicant_name(tool_context: ToolContext) -> str:
    """
    invocation_stateから申請者名を取得する。
    
    Args:
        tool_context: AWS Strandsのツールコンテキスト
        
    Returns:
        str: 申請者名（取得できない場合は"未設定"）
    """
```

**責任**: ToolContextから申請者名を安全に取得する

**入力**: ToolContext
**出力**: str（申請者名または"未設定"）

#### 1.2 ファイル名生成関数

```python
def _generate_filename(prefix: str) -> str:
    """
    タイムスタンプ付きのファイル名を生成する。
    
    Args:
        prefix: ファイル名のプレフィックス（例: "経費精算申請書", "交通費申請書"）
        
    Returns:
        str: タイムスタンプ付きファイル名（例: "経費精算申請書_20240115_143022.xlsx"）
    """
```

**責任**: 一意なファイル名を生成する

**入力**: str（プレフィックス）
**出力**: str（タイムスタンプ付きファイル名）

**フォーマット**: `{prefix}_YYYYMMDD_HHMMSS.xlsx`

#### 1.3 出力ディレクトリ確保関数

```python
def _ensure_output_directory() -> Path:
    """
    出力ディレクトリを作成し、そのパスを返す。
    
    Returns:
        Path: 出力ディレクトリのパス（output/）
    """
```

**責任**: 出力ディレクトリの存在を保証する

**入力**: なし
**出力**: Path（output/ディレクトリ）

**動作**: ディレクトリが存在しない場合は作成する

#### 1.4 ワークブック作成関数

```python
def _create_workbook(title: str) -> tuple[Workbook, Worksheet]:
    """
    新しいExcelワークブックとワークシートを作成する。
    
    Args:
        title: ワークシートのタイトル
        
    Returns:
        tuple: (Workbook, Worksheet)のタプル
    """
```

**責任**: 基本的なExcelワークブックを初期化する

**入力**: str（シートタイトル）
**出力**: tuple[Workbook, Worksheet]

#### 1.5 スタイル定義作成関数

```python
def _create_style_definitions() -> dict:
    """
    Excel用の共通スタイル定義を作成する。
    
    Returns:
        dict: スタイルオブジェクトの辞書
            - header_font: ヘッダー用フォント
            - header_fill: ヘッダー用背景色
            - header_alignment: ヘッダー用配置
            - title_font: タイトル用フォント
            - title_alignment: タイトル用配置
            - label_font: ラベル用フォント
            - label_fill: ラベル用背景色
            - data_alignment_center: データ中央揃え
            - data_alignment_right: データ右揃え
            - total_font: 合計用フォント
            - total_alignment: 合計用配置
    """
```

**責任**: 一貫したスタイル定義を提供する

**入力**: なし
**出力**: dict（スタイルオブジェクトのマップ）

**スタイル仕様**:
- ヘッダーフォント: 太字、12pt
- ヘッダー背景色: #CCE5FF（薄い青）
- タイトルフォント: 太字、14pt
- 配置: 中央揃え、右揃え

#### 1.6 ヘッダースタイル適用関数

```python
def _apply_header_style(cell, styles: dict) -> None:
    """
    セルにヘッダースタイルを適用する。
    
    Args:
        cell: openpyxlのセルオブジェクト
        styles: _create_style_definitions()で作成したスタイル辞書
    """
```

**責任**: セルにヘッダースタイルを一括適用する

**入力**: Cell, dict
**出力**: なし（セルを直接変更）

#### 1.7 タイトルスタイル適用関数

```python
def _apply_title_style(cell, styles: dict) -> None:
    """
    セルにタイトルスタイルを適用する。
    
    Args:
        cell: openpyxlのセルオブジェクト
        styles: _create_style_definitions()で作成したスタイル辞書
    """
```

**責任**: セルにタイトルスタイルを一括適用する

**入力**: Cell, dict
**出力**: なし（セルを直接変更）

#### 1.8 ワークブック保存関数

```python
def _save_workbook(wb: Workbook, file_path: Path) -> bool:
    """
    ワークブックをファイルに保存する。
    
    Args:
        wb: 保存するワークブック
        file_path: 保存先のファイルパス
        
    Returns:
        bool: 保存成功時True、失敗時False
    """
```

**責任**: ワークブックを安全にファイルに保存する

**入力**: Workbook, Path
**出力**: bool（成功/失敗）

**エラーハンドリング**: IOErrorやPermissionErrorをキャッチ

### 2. 公開ツール関数

#### 2.1 receipt_excel_generator

**インターフェース**: 変更なし（既存のパラメータと戻り値を維持）

**リファクタリング内容**:
- 共通ヘルパー関数を使用してコードを簡潔化
- 領収書固有のロジック（金額チェック、品目リスト表示）のみを保持

**処理フロー**:
1. `_get_applicant_name()`で申請者名を取得
2. 金額チェック（ApprovalRuleEngine使用）
3. `_generate_filename("経費精算申請書")`でファイル名生成
4. `_ensure_output_directory()`で出力ディレクトリ確保
5. `_create_workbook("経費精算申請書")`でワークブック作成
6. `_create_style_definitions()`でスタイル取得
7. 領収書データの入力（固有ロジック）
8. `_save_workbook()`でファイル保存
9. 結果辞書を返す

#### 2.2 travel_excel_generator

**インターフェース**: 変更なし（既存のパラメータと戻り値を維持）

**リファクタリング内容**:
- 共通ヘルパー関数を使用してコードを簡潔化
- 交通費固有のロジック（経路テーブル、合計計算）のみを保持

**処理フロー**:
1. `_get_applicant_name()`で申請者名を取得
2. データバリデーション（RouteInput使用）
3. `_generate_filename("交通費申請書")`でファイル名生成
4. `_ensure_output_directory()`で出力ディレクトリ確保
5. `_create_workbook("交通費申請書")`でワークブック作成
6. `_create_style_definitions()`でスタイル取得
7. 交通費データの入力（固有ロジック）
8. `_save_workbook()`でファイル保存
9. 結果辞書を返す

## Data Models

### 入力データモデル

#### Receipt Excel Generator Input

```python
{
    "store_name": str,           # 店舗名
    "amount": float,             # 金額（円）
    "date": str,                 # 日付（YYYY-MM-DD形式）
    "items": List[str],          # 品目リスト
    "expense_category": str,     # 経費区分
    "tool_context": ToolContext  # AWS Strandsコンテキスト
}
```

#### Travel Excel Generator Input

```python
{
    "routes": List[dict],        # 経路データリスト
    "tool_context": ToolContext  # AWS Strandsコンテキスト
}

# 各経路データの構造（RouteInputモデル）
{
    "departure": str,            # 出発地
    "destination": str,          # 目的地
    "date": str,                 # 日付（YYYY-MM-DD形式）
    "transport_type": str,       # 交通手段（train/bus/taxi/airplane）
    "cost": float,               # 費用
    "notes": str (optional)      # 備考
}
```

### 出力データモデル

#### Receipt Excel Generator Output

```python
{
    "success": bool,             # 成功フラグ
    "file_path": str,            # 保存されたファイルのパス
    "message": str               # 結果メッセージ
}
```

#### Travel Excel Generator Output

```python
{
    "success": bool,             # 成功フラグ
    "file_path": str,            # 保存されたファイルのパス
    "total_cost": float,         # 合計交通費
    "message": str               # 結果メッセージ
}
```

### 内部データモデル

#### Style Definitions

```python
{
    "header_font": Font,         # 太字、12pt
    "header_fill": PatternFill,  # #CCE5FF
    "header_alignment": Alignment, # 中央揃え
    "title_font": Font,          # 太字、14pt
    "title_alignment": Alignment, # 中央揃え
    "label_font": Font,          # 太字、12pt
    "label_fill": PatternFill,   # #CCE5FF
    "data_alignment_center": Alignment, # 中央揃え
    "data_alignment_right": Alignment,  # 右揃え
    "total_font": Font,          # 太字、12pt
    "total_alignment": Alignment # 右揃え
}
```

### データフロー

```
1. エージェント → ツール関数
   - パラメータとToolContextを渡す

2. ツール関数 → ヘルパー関数
   - 共通処理を委譲

3. ヘルパー関数 → openpyxl
   - Excelオブジェクトを操作

4. ツール関数 → ファイルシステム
   - Excelファイルを保存

5. ツール関数 → エージェント
   - 結果辞書を返す
```


## Correctness Properties

プロパティとは、システムの全ての有効な実行において真であるべき特性や動作のことです。プロパティは、人間が読める仕様と機械が検証可能な正確性保証の橋渡しとなります。

以下のプロパティは、リファクタリング後のExcel Generatorが満たすべき普遍的な特性を定義します。各プロパティは、プロパティベーステストとして実装され、多数の生成された入力に対して検証されます。

### Property 1: 申請者名の正確な取得

*For any* ToolContextオブジェクトで、invocation_stateに申請者名が設定されている場合、`_get_applicant_name()`は設定された申請者名を正確に返すべきである。invocation_stateが存在しないか申請者名が設定されていない場合は、"未設定"を返すべきである。

**Validates: Requirements 1.1**

### Property 2: ファイル名フォーマットの一貫性

*For any* プレフィックス文字列に対して、`_generate_filename(prefix)`は以下の条件を満たすファイル名を返すべきである：
- プレフィックスで始まる
- アンダースコアで区切られたタイムスタンプ（YYYYMMDD_HHMMSS形式）を含む
- .xlsx拡張子で終わる
- フォーマット: `{prefix}_YYYYMMDD_HHMMSS.xlsx`

**Validates: Requirements 1.2**

### Property 3: 出力ディレクトリへの保存

*For any* 有効な入力データに対して、`receipt_excel_generator()`または`travel_excel_generator()`を実行した場合、成功時に返される`file_path`は`output/`ディレクトリ内のパスであるべきである。

**Validates: Requirements 1.3**

### Property 4: 戻り値構造の完全性

*For any* 入力データ（有効または無効）に対して、`receipt_excel_generator()`または`travel_excel_generator()`の戻り値は以下のキーを含む辞書であるべきである：
- `success` (bool): 処理の成功/失敗を示す
- `file_path` (str): 生成されたファイルのパス（失敗時は空文字列）
- `message` (str): 結果メッセージ

さらに、`travel_excel_generator()`の場合は`total_cost` (float)も含むべきである。

**Validates: Requirements 1.4**

### Property 5: スタイル定義の完全性

*For any* 実行において、`_create_style_definitions()`が返す辞書は以下の全てのキーを含むべきである：
- `header_font`
- `header_fill`
- `header_alignment`
- `title_font`
- `title_alignment`
- `label_font`
- `label_fill`
- `data_alignment_center`
- `data_alignment_right`
- `total_font`
- `total_alignment`

各値は対応するopenpyxlスタイルオブジェクト（Font、PatternFill、Alignment）であるべきである。

**Validates: Requirements 1.5**

### Property 6: エラー時の戻り値構造

*For any* 不正な入力データ（空の経路リスト、不正な日付フォーマット、バリデーションエラーなど）に対して、`receipt_excel_generator()`または`travel_excel_generator()`は以下の条件を満たす辞書を返すべきである：
- `success`が`False`である
- `message`にエラー説明が含まれる（空でない文字列）
- `file_path`が空文字列である

**Validates: Requirements 3.1**

### Property 7: 日本語エラーメッセージ

*For any* エラーケース（バリデーションエラー、ファイル保存エラーなど）において、`receipt_excel_generator()`または`travel_excel_generator()`が返す`message`は日本語文字（ひらがな、カタカナ、または漢字）を含むべきである。

**Validates: Requirements 3.3**

## Error Handling

### エラーカテゴリと処理戦略

#### 1. バリデーションエラー

**発生条件**:
- 空の経路リスト
- 不正な日付フォーマット
- 必須フィールドの欠落
- 金額が上限を超える（receipt_excel_generatorの場合）

**処理方法**:
- `success: False`を含む辞書を返す
- 具体的なエラー内容を日本語で`message`に含める
- `file_path`は空文字列
- 例外を投げない（ValueErrorは金額チェックのみ）

**実装例**:
```python
if not routes:
    return {
        "success": False,
        "file_path": "",
        "total_cost": 0,
        "message": "エラー: 経路データが空です"
    }
```

#### 2. ファイルシステムエラー

**発生条件**:
- ディレクトリ作成の失敗
- ファイル保存の失敗（権限エラー、ディスク容量不足など）

**処理方法**:
- try-exceptブロックでIOError、PermissionErrorをキャッチ
- `success: False`を含む辞書を返す
- エラーの種類を日本語で`message`に含める
- 部分的に作成されたファイルのクリーンアップ（必要に応じて）

**実装例**:
```python
try:
    wb.save(file_path)
    return {"success": True, ...}
except (IOError, PermissionError) as e:
    return {
        "success": False,
        "file_path": "",
        "message": f"ファイル保存エラー: {str(e)}"
    }
```

#### 3. ToolContextエラー

**発生条件**:
- tool_contextがNone
- invocation_stateが存在しない

**処理方法**:
- デフォルト値（"未設定"）を使用
- 処理を継続（エラーとして扱わない）
- ログに警告を記録（オプション）

**実装例**:
```python
def _get_applicant_name(tool_context: ToolContext) -> str:
    if not tool_context or not tool_context.invocation_state:
        return "未設定"
    return tool_context.invocation_state.get("applicant_name", "未設定")
```

#### 4. Pydanticバリデーションエラー

**発生条件**:
- RouteInputモデルのバリデーション失敗
- 不正なデータ型
- 制約違反

**処理方法**:
- ValidationErrorをキャッチ
- エラー詳細を日本語で整形
- どのフィールドが問題かを明示
- `success: False`を含む辞書を返す

**実装例**:
```python
try:
    validated_route = RouteInput(**route)
except ValidationError as e:
    error_messages = []
    for error in e.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        error_messages.append(f"{field}: {error['msg']}")
    return {
        "success": False,
        "message": f"バリデーションエラー: {', '.join(error_messages)}"
    }
```

### エラーメッセージの一貫性

全てのエラーメッセージは以下の原則に従う：

1. **日本語**: 全てのメッセージは日本語で記述
2. **具体性**: エラーの原因を明確に説明
3. **実行可能性**: 可能な限り、ユーザーが取るべきアクションを示唆
4. **一貫性**: 同じ種類のエラーには同じフォーマットを使用

**エラーメッセージの例**:
- `"エラー: 経路データが空です"`
- `"エラー: 経路1のデータが不正です - date: 日付フォーマットが不正です"`
- `"バリデーションエラー: cost: 数値である必要があります"`
- `"ファイル保存エラー: [Errno 13] Permission denied"`

## Testing Strategy

### テストアプローチ

このリファクタリングでは、**ユニットテスト**と**プロパティベーステスト**の両方を使用して包括的なテストカバレッジを実現します。

#### ユニットテスト

**目的**: 特定の例、エッジケース、エラー条件を検証

**対象**:
- 各ヘルパー関数の基本動作
- エラーハンドリングの具体例
- 既存のテストとの互換性確認
- 統合ポイント（エージェントとの連携）

**テストケース例**:
1. `_get_applicant_name()`がNoneのcontextで"未設定"を返す
2. `_generate_filename()`が正しいフォーマットのファイル名を生成する
3. `_ensure_output_directory()`がディレクトリを作成する
4. 空の経路リストでエラーが返される
5. 不正な日付フォーマットでバリデーションエラーが発生する
6. 既存のテスト（tests/test_tools.py）が全て合格する

#### プロパティベーステスト

**目的**: 普遍的なプロパティを多数の生成された入力で検証

**使用ライブラリ**: Hypothesis（Python用プロパティベーステストライブラリ）

**設定**:
- 最小実行回数: 100イテレーション
- 各テストにはデザインドキュメントのプロパティ番号を参照するタグを付ける
- タグフォーマット: `# Feature: excel-generator-refactoring, Property {N}: {property_text}`

**プロパティテスト実装計画**:

1. **Property 1: 申請者名の正確な取得**
   - 生成: ランダムなToolContextオブジェクト（invocation_stateあり/なし）
   - 検証: 返される申請者名が期待値と一致する

2. **Property 2: ファイル名フォーマットの一貫性**
   - 生成: ランダムなプレフィックス文字列
   - 検証: 返されるファイル名が正規表現パターンに一致する

3. **Property 3: 出力ディレクトリへの保存**
   - 生成: ランダムな有効入力データ
   - 検証: file_pathが"output/"で始まる

4. **Property 4: 戻り値構造の完全性**
   - 生成: ランダムな入力データ（有効/無効）
   - 検証: 戻り値が必須キーを全て含む

5. **Property 5: スタイル定義の完全性**
   - 生成: なし（決定的テスト）
   - 検証: 返される辞書が全てのスタイルキーを含む

6. **Property 6: エラー時の戻り値構造**
   - 生成: ランダムな不正入力データ
   - 検証: success=False、messageが非空、file_pathが空

7. **Property 7: 日本語エラーメッセージ**
   - 生成: ランダムなエラーケース
   - 検証: messageに日本語文字が含まれる

### テスト実行戦略

#### 開発フェーズ

1. **ヘルパー関数の実装**
   - 各ヘルパー関数を実装
   - 対応するユニットテストを作成して実行
   - プロパティテストを作成して実行

2. **公開関数のリファクタリング**
   - receipt_excel_generatorをリファクタリング
   - 既存のテストが合格することを確認
   - 新しいプロパティテストを実行

3. **統合テスト**
   - 両方のツール関数が正しく動作することを確認
   - エージェントとの統合を手動でテスト

#### 継続的テスト

- 全てのテスト（ユニット + プロパティ）をCIパイプラインで実行
- プロパティテストは最低100イテレーションで実行
- テスト失敗時は詳細なエラーレポートを生成

### テストカバレッジ目標

- **行カバレッジ**: 90%以上
- **分岐カバレッジ**: 85%以上
- **関数カバレッジ**: 100%（全てのヘルパー関数と公開関数）

### 既存テストとの互換性

リファクタリング後も、`tests/test_tools.py`の`TestExcelGeneratorTools`クラスの全てのテストが合格する必要があります。これにより、以下が保証されます：

1. 既存のエージェントが引き続き動作する
2. ツールのインターフェースが変更されていない
3. 戻り値の構造が維持されている
4. エラーハンドリングが一貫している

**検証方法**:
```bash
python -m pytest tests/test_tools.py::TestExcelGeneratorTools -v
```

全てのテストが合格することを確認してから、リファクタリングを完了とします。
