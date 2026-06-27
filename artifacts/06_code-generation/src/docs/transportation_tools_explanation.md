# transportation_tools.py 解説

## このファイルの役割

交通費精算エージェントが使う**運賃計算ツール**です。出発地・目的地・交通手段・移動日を受け取り、JSONファイルに登録された運賃データを参照して金額を返します。

```
交通費精算エージェント（LLM）
  │  「calculate_transportation_cost を呼ぼう」
  ▼
calculate_transportation_cost()    ← このファイルの主役
  │
  ├─ 電車の場合  → train_fares.json  を参照
  └─ その他の場合 → fixed_fares.json を参照
```

---

## 1. @tool デコレータと戻り値の設計

### 1-1. @tool(context=True)

```python
# tools/transportation_tools.py  101〜108行
@tool(context=True)
def calculate_transportation_cost(
    departure: str,
    destination: str,
    transport_type: str,
    travel_date: str,
    tool_context: ToolContext,
) -> dict:
```

`@tool(context=True)` で Strands にツールとして登録します。`transportation_expense_agent.py` と同じ仕組みです。LLMはこの関数の名前・引数・docstring を読んで「いつ呼ぶか」を判断します。

`context=True` により `tool_context` 引数は Strands が自動で注入します。LLMが呼び出す際に指定するのは `departure` / `destination` / `transport_type` / `travel_date` の4つだけです。

---

### 1-2. 戻り値を dict にする理由

```python
return {"success": True, "fare": 320, "error_message": None, "is_expired": False}
```

戻り値の構造を整理します。

| キー | 型 | 意味 |
|------|-----|------|
| `success` | bool | 計算が成功したか |
| `fare` | int \| None | 運賃（円）。失敗時は None |
| `error_message` | str \| None | 失敗の理由。成功時は None |
| `is_expired` | bool \| None | 申請期限を超過しているか |

**なぜ例外を投げずに `dict` で返すのか？**

LLM はツールの戻り値をテキストとして受け取ります。Python の例外はそのままでは LLM に伝わりません。`success: False` と `error_message` を含む辞書を返すことで、LLM が「計算できなかった理由」を理解し、ユーザーへの適切な応答（「この経路は登録されていません。実際の金額を教えてください」など）を生成できます。

```
成功時: {"success": True,  "fare": 320,  "error_message": None,  "is_expired": False}
失敗時: {"success": False, "fare": None, "error_message": "...", "is_expired": None}
```

---

## 2. モジュールレベルのキャッシュ

### 2-1. キャッシュ変数の宣言

```python
# tools/transportation_tools.py  25〜29行
_train_fares: list = []
_train_fares_loaded: bool = False

_fixed_fares: dict = {}
_fixed_fares_loaded: bool = False
```

これらは関数の外（モジュールレベル）で宣言された変数です。モジュールレベルの変数はプログラムが起動してから終了するまで、**値が保持され続けます**。

---

### 2-2. フラグで二重読み込みを防ぐ

```python
# tools/transportation_tools.py  39〜70行
def _load_train_fares() -> tuple[bool, str]:
    global _train_fares, _train_fares_loaded

    if _train_fares_loaded:        # ← すでに読み込み済みなら即リターン
        return (True, "")

    # ...ファイルを読み込む処理...
    _train_fares = validated
    _train_fares_loaded = True     # ← 読み込み完了フラグを立てる
    return (True, "")
```

`_train_fares_loaded` が `True` なら処理を飛ばして既存のデータを使います。

```
1回目の呼び出し: _train_fares_loaded = False → ファイルを読む → フラグを True にする
2回目の呼び出し: _train_fares_loaded = True  → ファイルを読まずにスキップ
3回目以降:      同上
```

運賃データは申請のたびに変わるものではないので、一度読めばそれを使い続けることでファイル読み込みのコストを省けます。

---

### 2-3. global キーワード

```python
global _train_fares, _train_fares_loaded
```

Python では関数の中からモジュールレベルの変数に**書き込む**には `global` 宣言が必要です。読み込むだけなら不要ですが、`_train_fares = validated` や `_train_fares_loaded = True` のように値を上書きするためここで宣言しています。

---

## 3. JSON ファイルの読み込み

```python
# tools/transportation_tools.py  54〜67行
with open(_TRAIN_FARES_PATH, encoding="utf-8") as f:
    data = json.load(f)

routes = data.get("routes", data) if isinstance(data, dict) else data

validated = []
for item in routes:
    validated.append(RouteData(**item))
```

3つのステップに分かれています。

**① `json.load(f)` でファイルを Python オブジェクトに変換**

```
train_fares.json の中身（例）         json.load() 後
{                              →      {"routes": [
  "routes": [                           {"departure": "東京", "destination": "新宿", "fare": 200},
    {"departure": "東京", ...}            ...
  ]                                   ]}
}
```

**② `data.get("routes", data)` で柔軟にリストを取り出す**

```python
routes = data.get("routes", data) if isinstance(data, dict) else data
```

| JSONの構造 | `isinstance(data, dict)` | 結果 |
|-----------|--------------------------|------|
| `{"routes": [...]}` | True | `data.get("routes", data)` → リストを取り出す |
| `[...]` （配列直接） | False | `data` をそのまま使う |

どちらの形式のJSONでも動くように書かれています。第2引数の `data` は `"routes"` キーがなかった場合のデフォルト値です。

**③ `RouteData(**item)` で Pydantic バリデーション**

辞書をそのままリストに追加するのではなく、`RouteData` モデルに通すことで型の正しさを保証します（後述）。

---

## 4. Pydantic バリデーション

### 4-1. TransportCalculatorInput で入力を検証

```python
# tools/transportation_tools.py  133〜147行
try:
    validated = TransportCalculatorInput(
        departure=departure,
        destination=destination,
        transport_type=transport_type,
        travel_date=travel_date,
    )
except ValidationError as e:
    return {
        "success": False,
        "fare": None,
        "error_message": ErrorHandler.handle_validation_error(e),
        "is_expired": None,
    }
```

`TransportCalculatorInput` は `models/data_models.py` に定義された Pydantic モデルです。

```python
# models/data_models.py  166〜181行
class TransportCalculatorInput(BaseModel):
    departure: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    transport_type: Literal["電車", "バス", "タクシー", "飛行機"]  # ← 許可値を限定
    travel_date: str

    @field_validator("transport_type", mode="before")
    def _normalize_transport_type(cls, v):
        return normalize_transport_type(v)   # "JR" → "電車" などを正規化

    @field_validator("travel_date", mode="before")
    def _validate_travel_date(cls, v):
        return validate_date(v)   # "2026/05/24" → "2026-05-24" に正規化
```

インスタンス生成時に自動で以下が走ります。

```
LLM が渡してきた値（自然言語由来）
  "JR"        →  normalize_transport_type()  →  "電車"
  "2026/5/24" →  validate_date()             →  "2026-05-24"
  "新幹線"    →  Literal チェックで ValidationError（許可値以外）
```

LLM が生成した文字列には表記ゆれが含まれることがあります。Pydantic を使うことで、その後の処理に渡る前に値を正規化・検証できます。

---

## 5. 申請期限チェック

```python
# tools/transportation_tools.py  149〜165行
application_date = tool_context.invocation_state.get("application_date")
is_expired = False
if application_date:
    try:
        app_dt   = datetime.strptime(application_date, "%Y-%m-%d")
        travel_dt = datetime.strptime(validated.travel_date, "%Y-%m-%d")
        deadline_months = settings.transportation_expense.deadline_months
        deadline_dt = app_dt - relativedelta(months=deadline_months)
        if travel_dt < deadline_dt:
            is_expired = True
    except Exception:
        pass
```

「移動日が申請期限より古すぎないか」をここで判定します。

**なぜ `timedelta` ではなく `relativedelta` を使うのか**

```python
# timedelta の場合（日数換算なので月によって結果がズレる）
app_dt - timedelta(days=90)   # 3ヶ月 = 90日と仮定するしかない

# relativedelta の場合（暦通りに計算）
app_dt - relativedelta(months=3)  # 3月前を正確に返す
```

`relativedelta` は `dateutil` ライブラリが提供するクラスで、「3ヶ月前」を月の長さに関わらず正確に計算できます。

**期限の計算イメージ（deadline_months=3 の場合）**

```
申請日:   2026-05-24
期限:     2026-02-24  （3ヶ月前）

移動日が 2026-02-24 より前 → is_expired = True
移動日が 2026-02-24 以降  → is_expired = False
```

`is_expired` は運賃の計算結果と一緒に辞書で返され、LLM が「この移動は期限超過です」とユーザーに説明するために使います。

---

## 6. 交通手段による処理分岐

```python
# tools/transportation_tools.py  168〜209行
if validated.transport_type == "電車":
    # train_fares.json から経路を検索
    ok, err = _load_train_fares()
    ...
    fare = None
    for route in _train_fares:
        if route.departure == validated.departure and route.destination == validated.destination:
            fare = route.fare
            break
else:
    # fixed_fares.json から固定運賃を取得
    ok, err = _load_fixed_fares()
    ...
    fare_key = _TRANSPORT_TYPE_TO_KEY.get(validated.transport_type)
    fare = _fixed_fares[fare_key]
```

電車とそれ以外で参照するデータが異なります。

| 交通手段 | 参照ファイル | 仕組み |
|----------|-------------|--------|
| 電車 | `train_fares.json` | 出発地・目的地の組み合わせで検索 |
| バス・タクシー・飛行機 | `fixed_fares.json` | 交通手段ごとの固定金額を参照 |

**電車：線形探索で経路を検索**

```python
for route in _train_fares:
    if route.departure == validated.departure and route.destination == validated.destination:
        fare = route.fare
        break   # ← 見つかったら即終了
```

`_train_fares` は `RouteData` オブジェクトのリストです。先頭から順番に比較し、出発地と目的地が一致した最初のレコードの運賃を使います。`break` で余分な探索を止めています。

**電車：経路が見つからなかった場合**

```python
if fare is None:
    return {
        "success": False,
        "fare": None,
        "error_message": (
            f"{validated.departure}→{validated.destination}の経路が登録されていないため"
            "自動計算できません。実際にかかった金額をユーザーに確認してください。"
        ),
        "is_expired": is_expired,
    }
```

`error_message` に「ユーザーに確認してください」と書くことで、LLM がこのメッセージを読んで「金額を入力してください」とユーザーに問いかけるよう誘導しています。

**バス・タクシー・飛行機：マッピング辞書で変換**

```python
# tools/transportation_tools.py  31〜36行
_TRANSPORT_TYPE_TO_KEY = {
    "バス": "bus",
    "タクシー": "taxi",
    "飛行機": "airplane",
}

fare_key = _TRANSPORT_TYPE_TO_KEY.get(validated.transport_type)
fare = _fixed_fares[fare_key]
```

`fixed_fares.json` のキーは英語（`"bus"`, `"taxi"`, `"airplane"`）です。日本語の交通手段名を辞書で英語キーに変換してから参照します。

---

## 7. ロギング

```python
_logger = logging.getLogger(__name__)
```

ファイル先頭でロガーを取得しています。`__name__` はモジュール名（`tools.transportation_tools`）になるので、ログを見たときにどのファイルからの出力か一目でわかります。

使い分けのルールは以下の通りです。

| メソッド | 使用箇所 | 意味 |
|----------|----------|------|
| `_logger.info(...)` | 計算開始・完了・データ読み込み完了 | 正常な処理の記録 |
| `_logger.warning(...)` | ファイル未発見・申請期限超過 | 異常ではないが注意が必要な状態 |
| `_logger.error(..., exc_info=True)` | 例外が発生した箇所 | 調査が必要なエラーの記録 |

`exc_info=True` を付けると、例外のスタックトレース（どのコードで何が起きたかの詳細）もログに出力されます。バグ調査のときに役立ちます。

---

## まとめ：calculate_transportation_cost() の処理フロー

```
引数を受け取る（departure, destination, transport_type, travel_date）
  │
  ▼
① TransportCalculatorInput でバリデーション・正規化
  │ 失敗 → {"success": False, "error_message": "..."} を返す
  │
  ▼
② tool_context.invocation_state から申請日を取得し、期限チェック
  │
  ▼
③ 交通手段で分岐
  ├─ 電車  → _load_train_fares() → 出発地・目的地で線形探索
  │           見つからない → {"success": False, "error_message": "金額を確認して"} を返す
  │
  └─ その他 → _load_fixed_fares() → マッピング辞書で英語キーに変換 → 固定運賃を取得
  │
  ▼
④ {"success": True, "fare": 320, "is_expired": False} を返す
```
