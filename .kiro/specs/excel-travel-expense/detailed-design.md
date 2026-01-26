# 交通費申請書Excel生成機能 詳細設計書

## 1. 関数仕様

### 1.1 関数シグネチャ

```python
@tool
def generate_travel_excel(
    routes: List[dict],
    user_id: str = "0001"
) -> dict:
    """
    交通費申請書をExcel形式で生成する。
    
    このツールは交通費の経路データからExcel申請書を作成します。
    複数の経路を一覧表形式で表示し、合計交通費を計算します。
    
    Args:
        routes: 経路データのリスト。各要素は以下のキーを持つ辞書:
            - departure (str): 出発地
            - destination (str): 目的地
            - date (str): 日付（YYYY-MM-DD形式）
            - transport_type (str): 交通手段 (train/bus/taxi/airplane)
            - cost (float): 費用
            - notes (str, optional): 備考
        user_id: ユーザー識別子（デフォルト: "0001"）
    
    Returns:
        dict: {
            "success": bool,         # 成功フラグ
            "file_path": str,        # 保存されたファイルのパス
            "total_cost": float,     # 合計交通費
            "message": str           # 結果メッセージ
        }
    """
```

---

## 2. 実装の流れ（ステップバイステップ）

### ステップ1：入力検証
### ステップ2：初期設定
### ステップ3：Excelワークブック作成
### ステップ4：スタイル定義
### ステップ5：タイトル行の作成
### ステップ6：申請者情報の作成
### ステップ7：テーブルヘッダーの作成
### ステップ8：データ行の作成
### ステップ9：合計行の作成
### ステップ10：列幅調整とファイル保存
### ステップ11：戻り値の返却

---

## 3. 各ステップの詳細実装


### ステップ1：入力検証

#### 目的
不正なデータを早期に検出し、エラーメッセージを返す

#### 実装コード

```python
try:
    # 1-1. routesが空リストかチェック
    if not routes:
        return {
            "success": False,
            "file_path": "",
            "total_cost": 0,
            "message": "エラー: 経路データが空です"
        }
    
    # 1-2. routesがリスト型かチェック
    if not isinstance(routes, list):
        return {
            "success": False,
            "file_path": "",
            "total_cost": 0,
            "message": f"エラー: routesはリストである必要があります（受信: {type(routes).__name__}）"
        }
    
    # 1-3. 各経路データの必須キーをチェック
    required_keys = ["departure", "destination", "transport_type", "cost"]
    for i, route in enumerate(routes):
        # 辞書型かチェック
        if not isinstance(route, dict):
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": f"エラー: 経路{i+1}が辞書形式ではありません"
            }
        
        # 必須キーの存在チェック
        missing_keys = [key for key in required_keys if key not in route]
        if missing_keys:
            return {
                "success": False,
                "file_path": "",
                "total_cost": 0,
                "message": f"エラー: 経路{i+1}に必須キーが不足しています: {missing_keys}"
            }

except Exception as e:
    return {
        "success": False,
        "file_path": "",
        "total_cost": 0,
        "message": f"エラー: {str(e)}"
    }
```

#### チェック項目
- [ ] `routes`が空リストでないか
- [ ] `routes`がリスト型か
- [ ] 各経路が辞書型か
- [ ] 必須キー（departure, destination, transport_type, cost）が存在するか

---

### ステップ2：初期設定

#### 目的
ファイル名、出力パス、合計金額を準備する

#### 実装コード

```python
# 2-1. 合計交通費の計算
total_cost = sum(float(route.get("cost", 0)) for route in routes)

# 2-2. ファイル名の生成（タイムスタンプ付き）
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"交通費申請書_{timestamp}.xlsx"

# 2-3. 出力ディレクトリの作成
output_path = Path("output")
output_path.mkdir(parents=True, exist_ok=True)

# 2-4. 完全なファイルパスの生成
file_path = output_path / filename

# 2-5. 申請日の取得
report_date = datetime.now().strftime("%Y-%m-%d")
```

#### 変数一覧
| 変数名 | 型 | 説明 | 例 |
|--------|-----|------|-----|
| `total_cost` | float | 全経路の合計金額 | 15120.0 |
| `timestamp` | str | タイムスタンプ | "20260125_143022" |
| `filename` | str | ファイル名 | "交通費申請書_20260125_143022.xlsx" |
| `output_path` | Path | 出力ディレクトリ | Path("output") |
| `file_path` | Path | 完全なファイルパス | Path("output/交通費申請書_20260125_143022.xlsx") |
| `report_date` | str | 申請日 | "2026-01-25" |

---

### ステップ3：Excelワークブック作成

#### 目的
空のExcelワークブックとワークシートを作成する

#### 実装コード

```python
# 3-1. Excelワークブックの作成
wb = Workbook()

# 3-2. アクティブシートの取得
ws = wb.active

# 3-3. シート名の設定
ws.title = "交通費申請書"
```

#### 変数一覧
| 変数名 | 型 | 説明 |
|--------|-----|------|
| `wb` | Workbook | Excelワークブックオブジェクト |
| `ws` | Worksheet | アクティブなワークシート |

---

### ステップ4：スタイル定義

#### 目的
Excel内で使用するフォント、色、配置のスタイルを定義する

#### 実装コード

```python
# 4-1. ヘッダースタイル（テーブルヘッダー用）
header_font = Font(bold=True, size=12)
header_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")
header_alignment = Alignment(horizontal="center", vertical="center")

# 4-2. タイトルスタイル（最上部のタイトル用）
title_font = Font(bold=True, size=14)
title_alignment = Alignment(horizontal="center", vertical="center")

# 4-3. ラベルスタイル（申請者ID、申請日のラベル用）
label_font = Font(bold=True, size=12)
label_fill = PatternFill(start_color="CCE5FF", end_color="CCE5FF", fill_type="solid")

# 4-4. 合計行スタイル
total_font = Font(bold=True, size=12)
total_alignment = Alignment(horizontal="right", vertical="center")

# 4-5. データ行スタイル
data_alignment_center = Alignment(horizontal="center", vertical="center")
data_alignment_right = Alignment(horizontal="right", vertical="center")
```

#### スタイル一覧
| スタイル名 | 用途 | 設定内容 |
|-----------|------|---------|
| `header_font` | テーブルヘッダー | 太字・12pt |
| `header_fill` | テーブルヘッダー背景 | 水色（#CCE5FF） |
| `header_alignment` | テーブルヘッダー配置 | 中央揃え |
| `title_font` | タイトル | 太字・14pt |
| `title_alignment` | タイトル配置 | 中央揃え |
| `label_font` | ラベル | 太字・12pt |
| `label_fill` | ラベル背景 | 水色（#CCE5FF） |
| `total_font` | 合計行 | 太字・12pt |
| `total_alignment` | 合計行配置 | 右揃え |
| `data_alignment_center` | データ（中央） | 中央揃え |
| `data_alignment_right` | データ（右） | 右揃え |

---

### ステップ5：タイトル行の作成

#### 目的
Excelの最上部にタイトル「交通費申請書」を表示する

#### 実装コード

```python
# 5-1. タイトルテキストの設定（A1セル）
ws["A1"] = "交通費申請書"

# 5-2. タイトルのフォント設定
ws["A1"].font = title_font

# 5-3. タイトルの配置設定
ws["A1"].alignment = title_alignment

# 5-4. セルの結合（A1からF1まで）
ws.merge_cells("A1:F1")
```

#### セル配置
```
┌─────────────────────────────────┐
│ A1:F1 → 交通費申請書（結合）      │
└─────────────────────────────────┘
```

#### チェック項目
- [ ] A1セルに「交通費申請書」が設定されているか
- [ ] フォントが太字・14ptか
- [ ] 中央揃えになっているか
- [ ] A1:F1が結合されているか

---

### ステップ6：申請者情報の作成

#### 目的
申請者IDと申請日を表示する

#### 実装コード

```python
# 6-1. 現在の行番号を設定（タイトルの下、3行目から開始）
current_row = 3

# 6-2. 申請者IDのラベル（A列）
ws[f"A{current_row}"] = "申請者ID"
ws[f"A{current_row}"].font = label_font
ws[f"A{current_row}"].fill = label_fill

# 6-3. 申請者IDの値（B列）
ws[f"B{current_row}"] = user_id
current_row += 1

# 6-4. 申請日のラベル（A列）
ws[f"A{current_row}"] = "申請日"
ws[f"A{current_row}"].font = label_font
ws[f"A{current_row}"].fill = label_fill

# 6-5. 申請日の値（B列）
ws[f"B{current_row}"] = report_date
current_row += 1

# 6-6. 空行を追加
current_row += 1
```

#### セル配置
```
行3: │ 申請者ID（水色背景） │ 0001        │
行4: │ 申請日（水色背景）   │ 2026-01-25  │
行5: │ （空行）             │             │
```

#### 変数の変化
| ステップ | current_row | 説明 |
|---------|-------------|------|
| 初期値 | 3 | 申請者ID行 |
| +1後 | 4 | 申請日行 |
| +1後 | 5 | 空行 |
| +1後 | 6 | 次のステップ（テーブルヘッダー）へ |

---

### ステップ7：テーブルヘッダーの作成

#### 目的
経路データのテーブルヘッダー（列名）を作成する

#### 実装コード

```python
# 7-1. ヘッダー行の開始（current_rowは6）
header_row = current_row

# 7-2. 各列のヘッダーを設定
headers = ["No", "日付", "出発地", "目的地", "交通手段", "費用"]
columns = ["A", "B", "C", "D", "E", "F"]

for col, header_text in zip(columns, headers):
    cell = ws[f"{col}{header_row}"]
    cell.value = header_text
    cell.font = header_font
    cell.fill = header_fill
    cell.alignment = header_alignment

# 7-3. 次の行へ移動（データ行の開始位置）
current_row += 1
```

#### セル配置
```
行6: │ No │ 日付 │ 出発地 │ 目的地 │ 交通手段 │ 費用 │
     （すべて水色背景・太字・中央揃え）
```

#### ヘッダー一覧
| 列 | ヘッダー名 | 説明 |
|----|----------|------|
| A | No | 連番 |
| B | 日付 | 移動日 |
| C | 出発地 | 出発地名 |
| D | 目的地 | 目的地名 |
| E | 交通手段 | 電車/バス/タクシー/飛行機 |
| F | 費用 | 金額 |

---

### ステップ8：データ行の作成

#### 目的
各経路データをテーブルに1行ずつ追加する

#### 実装コード

```python
# 8-1. 交通手段の日本語マッピング
transport_map = {
    "train": "電車",
    "bus": "バス",
    "taxi": "タクシー",
    "airplane": "飛行機"
}

# 8-2. 各経路をループ処理
for i, route in enumerate(routes, start=1):
    # 8-3. No列（A列）：連番
    ws[f"A{current_row}"] = i
    ws[f"A{current_row}"].alignment = data_alignment_center
    
    # 8-4. 日付列（B列）
    ws[f"B{current_row}"] = route.get("date", "")
    ws[f"B{current_row}"].alignment = data_alignment_center
    
    # 8-5. 出発地列（C列）
    ws[f"C{current_row}"] = route["departure"]
    ws[f"C{current_row}"].alignment = data_alignment_center
    
    # 8-6. 目的地列（D列）
    ws[f"D{current_row}"] = route["destination"]
    ws[f"D{current_row}"].alignment = data_alignment_center
    
    # 8-7. 交通手段列（E列）：英語→日本語に変換
    transport_type = route["transport_type"]
    transport_name = transport_map.get(transport_type, transport_type)
    ws[f"E{current_row}"] = transport_name
    ws[f"E{current_row}"].alignment = data_alignment_center
    
    # 8-8. 費用列（F列）：通貨形式で表示
    ws[f"F{current_row}"] = f"¥{route['cost']:,.0f}"
    ws[f"F{current_row}"].alignment = data_alignment_right
    
    # 8-9. 次の行へ移動
    current_row += 1
```

#### データ例
```
行7: │ 1 │ 2026-01-25 │ 東京 │ 大阪 │ 電車 │ ¥13,620 │
行8: │ 2 │ 2026-01-26 │ 大阪 │ 京都 │ バス │ ¥1,500  │
```

#### 処理の流れ
1. `enumerate(routes, start=1)`で連番を生成（1から開始）
2. 各列にデータを設定
3. 交通手段は`transport_map`で日本語に変換
4. 費用は`¥`マークと3桁カンマ区切りで表示
5. `current_row`をインクリメントして次の行へ

---

### ステップ9：合計行の作成

#### 目的
全経路の合計交通費を表示する

#### 実装コード

```python
# 9-1. 空行を追加
current_row += 1

# 9-2. 合計ラベル（E列）
ws[f"E{current_row}"] = "合計交通費"
ws[f"E{current_row}"].font = total_font
ws[f"E{current_row}"].alignment = total_alignment

# 9-3. 合計金額（F列）
ws[f"F{current_row}"] = f"¥{total_cost:,.0f}"
ws[f"F{current_row}"].font = total_font
ws[f"F{current_row}"].alignment = total_alignment
```

#### セル配置
```
行9: │   │        │      │      │          │         │ （空行）
行10:│   │        │      │      │合計交通費│¥15,120  │
     （E列・F列は太字・右揃え）
```

#### チェック項目
- [ ] E列に「合計交通費」が表示されているか
- [ ] F列に合計金額が表示されているか
- [ ] 太字・右揃えになっているか
- [ ] 通貨形式（¥マーク・3桁カンマ）になっているか

---

### ステップ10：列幅調整とファイル保存

#### 目的
各列の幅を調整し、Excelファイルを保存する

#### 実装コード

```python
# 10-1. 列幅の調整
ws.column_dimensions["A"].width = 5   # No列
ws.column_dimensions["B"].width = 12  # 日付列
ws.column_dimensions["C"].width = 15  # 出発地列
ws.column_dimensions["D"].width = 15  # 目的地列
ws.column_dimensions["E"].width = 12  # 交通手段列
ws.column_dimensions["F"].width = 15  # 費用列

# 10-2. ファイルの保存
wb.save(file_path)
```

#### 列幅一覧
| 列 | 幅 | 理由 |
|----|-----|------|
| A (No) | 5 | 連番は短い |
| B (日付) | 12 | YYYY-MM-DD形式 |
| C (出発地) | 15 | 地名が入る |
| D (目的地) | 15 | 地名が入る |
| E (交通手段) | 12 | 「電車」「バス」など |
| F (費用) | 15 | ¥13,620など |

---

### ステップ11：戻り値の返却

#### 目的
処理結果を辞書形式で返す

#### 実装コード

```python
# 11-1. 成功時の戻り値
return {
    "success": True,
    "file_path": str(file_path),
    "total_cost": total_cost,
    "message": f"申請書を正常に作成しました: {file_path}"
}
```

#### 戻り値の例
```python
{
    "success": True,
    "file_path": "output/交通費申請書_20260125_143022.xlsx",
    "total_cost": 15120.0,
    "message": "申請書を正常に作成しました: output/交通費申請書_20260125_143022.xlsx"
}
```

---

## 4. 完全なコード構造

```python
@tool
def generate_travel_excel(routes: List[dict], user_id: str = "0001") -> dict:
    """docstring..."""
    try:
        # ステップ1: 入力検証
        # ...
        
        # ステップ2: 初期設定
        # ...
        
        # ステップ3: Excelワークブック作成
        # ...
        
        # ステップ4: スタイル定義
        # ...
        
        # ステップ5: タイトル行の作成
        # ...
        
        # ステップ6: 申請者情報の作成
        # ...
        
        # ステップ7: テーブルヘッダーの作成
        # ...
        
        # ステップ8: データ行の作成
        # ...
        
        # ステップ9: 合計行の作成
        # ...
        
        # ステップ10: 列幅調整とファイル保存
        # ...
        
        # ステップ11: 戻り値の返却
        return {...}
    
    except Exception as e:
        return {
            "success": False,
            "file_path": "",
            "total_cost": 0,
            "message": f"エラー: {str(e)}"
        }
```

---

## 5. テストデータ例

### 入力データ
```python
routes = [
    {
        "departure": "東京",
        "destination": "大阪",
        "date": "2026-01-25",
        "transport_type": "train",
        "cost": 13620.0
    },
    {
        "departure": "大阪",
        "destination": "京都",
        "date": "2026-01-26",
        "transport_type": "bus",
        "cost": 1500.0
    }
]

user_id = "0001"
```

### 期待される出力
```python
{
    "success": True,
    "file_path": "output/交通費申請書_20260125_143022.xlsx",
    "total_cost": 15120.0,
    "message": "申請書を正常に作成しました: output/交通費申請書_20260125_143022.xlsx"
}
```

---

## 6. 実装時のチェックリスト

### 各ステップ完了後の確認
- [ ] ステップ1: 入力検証が正しく動作するか
- [ ] ステップ2: ファイル名とパスが正しく生成されるか
- [ ] ステップ3: Excelワークブックが作成されるか
- [ ] ステップ4: スタイルが正しく定義されているか
- [ ] ステップ5: タイトルが正しく表示されるか
- [ ] ステップ6: 申請者情報が正しく表示されるか
- [ ] ステップ7: テーブルヘッダーが正しく表示されるか
- [ ] ステップ8: データ行が正しく表示されるか
- [ ] ステップ9: 合計行が正しく表示されるか
- [ ] ステップ10: 列幅が適切に調整されているか
- [ ] ステップ11: 戻り値が正しい形式か

### 最終確認
- [ ] Excelファイルが正しく保存されているか
- [ ] ファイルをExcelで開いて表示を確認
- [ ] 複数経路のデータで動作確認
- [ ] エラーケースの動作確認

---

## 7. よくあるエラーと対処法

### エラー1: `KeyError: 'cost'`
**原因**: 経路データに`cost`キーが存在しない  
**対処**: ステップ1の入力検証で必須キーをチェック

### エラー2: `TypeError: unsupported operand type(s) for +: 'int' and 'str'`
**原因**: `cost`が文字列型になっている  
**対処**: `float(route.get("cost", 0))`で型変換

### エラー3: ファイルが保存されない
**原因**: 出力ディレクトリが存在しない  
**対処**: `output_path.mkdir(parents=True, exist_ok=True)`で作成

### エラー4: 日本語が文字化けする
**原因**: Excelの文字コード問題  
**対処**: openpyxlは自動的にUTF-8で保存するため、通常は問題なし

---

## 8. 実装のヒント

### ヒント1: current_rowの管理
`current_row`変数で現在の行番号を追跡します。各セクション作成後に`current_row += 1`で次の行に移動します。

### ヒント2: f-stringの活用
セル参照には`f"{col}{row}"`形式を使います。例：`ws[f"A{current_row}"]`

### ヒント3: スタイルの再利用
同じスタイルを複数のセルに適用する場合、変数に格納して再利用します。

### ヒント4: デバッグ方法
各ステップ後に`print(f"current_row: {current_row}")`でデバッグできます。

---

## 9. 次のステップ

1. `tools/excel_generator.py`を開く
2. 既存の`excel_generator()`関数の下に新しい関数を追加
3. 必要なインポートを追加（既にあるはず）
4. ステップ1から順番に実装
5. 各ステップ完了後にテスト
6. 全ステップ完了後、実際のデータで動作確認

頑張ってください！
