# 交通費申請書Excel生成機能 基本設計書

## 1. 概要

### 1.1 目的
既存の`excel_generator.py`を拡張し、交通費申請書をExcel形式で生成する機能を追加する。

### 1.2 背景
- 現在、交通費申請書はPDF/JSON形式で生成されている（`report_tools.py`）
- 最終的にはExcel形式に統一し、PDF/JSON形式は廃止する
- 移行期間中は既存機能を残したまま、新機能を追加する

### 1.3 スコープ
- **対象**：交通費申請書のExcel生成機能の追加
- **対象外**：既存のPDF/JSON生成機能の削除（将来対応）

---

## 2. マージ方針

### 2.1 A案を採用：excel_generatorを拡張

**理由**：
- 領収書用と交通費用でレイアウトが異なる
- 別関数として実装することで、既存機能への影響を最小化
- 将来的な保守性が高い

**実装方針**：
```
tools/excel_generator.py
├── excel_generator()          # 既存：領収書用（変更なし）
└── generate_travel_excel()    # 新規：交通費用
```

### 2.2 ファイル構成

```
tools/
├── excel_generator.py         # 拡張対象
│   ├── excel_generator()      # 既存関数（領収書用）
│   └── generate_travel_excel() # 新規関数（交通費用）
├── report_tools.py            # 既存のまま残す（将来廃止予定）
└── fare_tools.py              # 変更なし
```

---

## 3. データ構造設計

### 3.1 入力データ構造

既存の`generate_report()`と同じデータ構造を使用：

```python
routes: List[dict]  # 経路データのリスト

# 各経路の構造
{
    "departure": str,        # 出発地（例: "東京"）
    "destination": str,      # 目的地（例: "大阪"）
    "date": str,            # 日付（YYYY-MM-DD形式）
    "transport_type": str,  # 交通手段（train/bus/taxi/airplane）
    "cost": float,          # 費用（例: 13620.0）
    "notes": str            # 備考（オプション）
}
```

### 3.2 関数シグネチャ

```python
@tool
def generate_travel_excel(
    routes: List[dict],
    user_id: str = "0001"
) -> dict:
    """
    交通費申請書をExcel形式で生成する。
    
    Args:
        routes: 経路データのリスト
        user_id: ユーザー識別子（デフォルト: "0001"）
    
    Returns:
        dict: {
            "success": bool,
            "file_path": str,
            "total_cost": float,
            "message": str
        }
    """
```

### 3.3 戻り値の構造

既存の`generate_report()`と同じ形式：

```python
{
    "success": True,                           # 成功フラグ
    "file_path": "output/交通費申請書_20260125_143022.xlsx",
    "total_cost": 15120.0,                     # 合計交通費
    "message": "申請書を正常に作成しました: ..."
}
```

---

## 4. Excelレイアウト設計

### 4.1 全体構成

```
┌─────────────────────────────────────────────────────────┐
│                    交通費申請書                          │  ← タイトル（A1:F1結合）
├──────────────┬──────────────────────────────────────────┤
│ 申請者ID      │ 0001                                     │
│ 申請日        │ 2026-01-25                               │
├──────────────┴──────────────────────────────────────────┤
│                                                          │  ← 空行
├────┬──────┬──────┬──────┬──────────┬─────────────────┤
│ No │ 日付  │ 出発地│ 目的地│ 交通手段  │ 費用            │  ← ヘッダー行
├────┼──────┼──────┼──────┼──────────┼─────────────────┤
│ 1  │2026- │東京  │大阪  │電車      │¥13,620          │
│    │01-25 │      │      │          │                 │
├────┼──────┼──────┼──────┼──────────┼─────────────────┤
│ 2  │2026- │大阪  │京都  │バス      │¥1,500           │
│    │01-26 │      │      │          │                 │
├────┼──────┼──────┼──────┼──────────┼─────────────────┤
│    │      │      │      │          │                 │  ← 空行
├────┴──────┴──────┴──────┴──────────┼─────────────────┤
│                          合計交通費  │¥15,120          │  ← 太字・大きめ
└─────────────────────────────────────┴─────────────────┘
```

### 4.2 セル配置詳細

#### ヘッダー部分
| セル | 内容 | スタイル |
|------|------|---------|
| A1:F1 | 交通費申請書 | 太字・14pt・中央揃え・結合 |
| A3 | 申請者ID | 太字・水色背景 |
| B3 | {user_id} | 通常 |
| A4 | 申請日 | 太字・水色背景 |
| B4 | {申請日} | 通常 |

#### テーブルヘッダー（6行目）
| セル | 内容 | 幅 | スタイル |
|------|------|-----|---------|
| A6 | No | 5 | 太字・水色背景・中央揃え |
| B6 | 日付 | 12 | 太字・水色背景・中央揃え |
| C6 | 出発地 | 15 | 太字・水色背景・中央揃え |
| D6 | 目的地 | 15 | 太字・水色背景・中央揃え |
| E6 | 交通手段 | 12 | 太字・水色背景・中央揃え |
| F6 | 費用 | 15 | 太字・水色背景・中央揃え |

#### データ行（7行目以降）
- 各経路を1行ずつ表示
- No列：連番（中央揃え）
- 費用列：通貨形式（¥13,620）・右揃え

#### 合計行
| セル | 内容 | スタイル |
|------|------|---------|
| E{最終行} | 合計交通費 | 太字・12pt・右揃え |
| F{最終行} | ¥{合計金額} | 太字・12pt・通貨形式・右揃え |

### 4.3 スタイル定義

```python
# ヘッダースタイル
header_font = Font(bold=True, size=12)
header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
header_alignment = Alignment(horizontal="center", vertical="center")

# タイトルスタイル
title_font = Font(bold=True, size=14)
title_alignment = Alignment(horizontal="center", vertical="center")

# 合計行スタイル
total_font = Font(bold=True, size=12)
total_alignment = Alignment(horizontal="right", vertical="center")

# データ行スタイル
data_alignment_center = Alignment(horizontal="center", vertical="center")
data_alignment_right = Alignment(horizontal="right", vertical="center")
```

### 4.4 交通手段の表示マッピング

```python
transport_map = {
    "train": "電車",
    "bus": "バス",
    "taxi": "タクシー",
    "airplane": "飛行機"
}
```

---

## 5. 実装詳細

### 5.1 ファイル名生成

```python
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"交通費申請書_{timestamp}.xlsx"
```

**例**：`交通費申請書_20260125_143022.xlsx`

### 5.2 出力ディレクトリ

```python
output_dir = "output"
```

既存の`report_tools.py`と同じディレクトリを使用

### 5.3 エラーハンドリング

#### 入力検証
1. `routes`が空リストの場合
2. `routes`がリスト型でない場合
3. 各経路に必須キーが不足している場合
4. データ型が不正な場合

#### エラー時の戻り値
```python
{
    "success": False,
    "file_path": "",
    "total_cost": 0,
    "message": "エラー: {詳細メッセージ}"
}
```

---

## 6. 既存機能との関係

### 6.1 既存機能の保持

**変更なし**：
- `tools/report_tools.py`の`generate_report()` → そのまま残す
- `tools/excel_generator.py`の`excel_generator()` → そのまま残す

**新規追加**：
- `tools/excel_generator.py`に`generate_travel_excel()`を追加

### 6.2 エージェントからの呼び出し

#### 現在（変更なし）
```python
# agents/travel_agent.py
from tools.report_tools import generate_report

tools=[
    calculate_fare,
    validate_input,
    generate_report  # 既存のPDF/JSON生成
]
```

#### 将来（Excel移行後）
```python
# agents/travel_agent.py
from tools.excel_generator import generate_travel_excel

tools=[
    calculate_fare,
    validate_input,
    generate_travel_excel  # 新しいExcel生成
]
```

---

## 7. 移行計画

### フェーズ1：Excel機能追加（今回）
- [ ] `generate_travel_excel()`を実装
- [ ] 既存機能は変更なし
- [ ] 動作確認・テスト

### フェーズ2：エージェント切り替え（次回）
- [ ] `travel_agent.py`のツール登録を変更
- [ ] システムプロンプトを更新（Excel形式のみ）
- [ ] 動作確認

### フェーズ3：旧機能削除（将来）
- [ ] `report_tools.py`のPDF/JSON生成機能を削除
- [ ] 不要な依存関係を削除（reportlab等）
- [ ] ドキュメント更新

---

## 8. テスト計画

### 8.1 単体テスト項目

1. **正常系**
   - 1件の経路データでExcel生成
   - 複数件の経路データでExcel生成
   - 備考なしのデータでExcel生成
   - 備考ありのデータでExcel生成

2. **異常系**
   - 空リストの場合
   - 必須キー不足の場合
   - データ型不正の場合

3. **スタイル確認**
   - ヘッダーの書式
   - テーブルの書式
   - 合計行の書式
   - 列幅の調整

### 8.2 統合テスト項目

1. エージェントからの呼び出し
2. 既存のPDF生成との比較（データ一致確認）
3. ファイル名の一意性確認

---

## 9. 依存関係

### 9.1 必要なライブラリ

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from datetime import datetime
from pathlib import Path
from typing import List
from strands import tool
```

### 9.2 既存の依存関係

- `openpyxl`：既に`excel_generator()`で使用中
- 追加インストール不要

---

## 10. 備考

### 10.1 既存のPDF出力との違い

| 項目 | PDF | Excel |
|------|-----|-------|
| レイアウト | 縦書き・リスト形式 | テーブル形式 |
| 編集可能性 | 不可 | 可能 |
| データ抽出 | 困難 | 容易 |
| 見た目 | 固定 | 柔軟 |

### 10.2 将来の拡張性

- 承認フロー機能の追加（承認欄の追加）
- 経費区分の追加
- 複数ユーザー対応
- テンプレート機能

---

## 11. 参考資料

- 既存実装：`tools/report_tools.py`
- 既存実装：`tools/excel_generator.py`
- データ構造：`generate_report()`の入力仕様
