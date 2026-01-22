# テストガイド

## 概要

このディレクトリには、マルチエージェント構成の申請代行システムのテストが含まれています。

## テストの種類

### 1. ユニットテスト (`test_tools.py`)
個々のツール関数の動作を検証します。

**テスト対象:**
- **交通費精算用ツール:**
  - `load_fare_data`: 運賃データの読み込み
  - `calculate_fare`: 運賃計算（電車、バス、タクシー、飛行機）
  - `validate_input`: 入力検証（日付、場所、金額）
  - `generate_report`: 申請書生成（PDF、JSON）
- **領収書精算用ツール:**
  - `excel_generator`: Excel申請書生成
  - `config_updater`: 設定更新

**テストケース数:** 約25件

### 2. エージェントテスト (`test_agent.py`)
各エージェントの基本機能を検証します。

**テスト対象:**
- **ReceptionAgent（オーケストレーター）:**
  - エージェントの初期化
  - 専門エージェントの登録確認
  - システムプロンプトの設定確認
- **TravelAgent（交通費精算）:**
  - Agents as Tools形式の動作確認
  - 会話履歴の管理
  - リセット機能
- **ReceiptExpenseAgent（領収書精算）:**
  - Agents as Tools形式の動作確認
  - ConfigManagerの統合

**テストケース数:** 約10件

### 3. 統合テスト (`test_integration.py`)
エンドツーエンドのワークフローを検証します。

**テスト対象:**
- 完全な交通費申請ワークフロー
- 完全な領収書精算ワークフロー
- マルチエージェント連携
- 複数の交通手段を使用したシナリオ
- エラーハンドリング

**テストケース数:** 約8件

## テストの実行方法

### 前提条件

必要なパッケージをインストールしてください：

```bash
pip install pytest
```

### すべてのテストを実行

```bash
pytest
```

または

```bash
python -m pytest
```

### 特定のテストファイルを実行

```bash
# ツールのテストのみ
pytest tests/test_tools.py

# エージェントのテストのみ
pytest tests/test_agent.py

# 統合テストのみ
pytest tests/test_integration.py
```

### 詳細な出力で実行

```bash
pytest -v
```

### 特定のテストクラスを実行

```bash
pytest tests/test_tools.py::TestFareTools
```

### 特定のテスト関数を実行

```bash
pytest tests/test_tools.py::TestFareTools::test_calculate_fare_train_valid
```

### カバレッジレポート付きで実行

```bash
# カバレッジパッケージをインストール
pip install pytest-cov

# カバレッジレポートを生成
pytest --cov=agents --cov=tools --cov=handlers --cov-report=html --cov-report=term-missing
```

HTMLレポートは `htmlcov/index.html` に生成されます。

## テスト結果の見方

### 成功例

```
tests/test_tools.py::TestFareTools::test_load_fare_data PASSED     [10%]
tests/test_tools.py::TestFareTools::test_calculate_fare_train_valid PASSED [20%]
```

### 失敗例

```
tests/test_tools.py::TestFareTools::test_calculate_fare_train_valid FAILED [20%]
```

失敗した場合は、詳細なエラーメッセージが表示されます。

## 注意事項

### LLM呼び出しが必要なテスト

一部のテストは、実際のLLM（Amazon Bedrock）を呼び出します。
これらのテストは以下の理由でスキップされています：

- AWS認証情報が必要
- 実行に時間がかかる
- APIコストが発生する

**対象テスト:**
- `test_agent.py`: エージェントの対話テスト
- `test_integration.py`: マルチエージェント連携テスト

手動でテストする場合は、テストコード内の `pytest.skip()` をコメントアウトしてください。

### マルチエージェント構成のテスト

システムはAgents as Toolsパターンで実装されています：
- **ReceptionAgent**: オーケストレーター（専門エージェントを振り分け）
- **TravelAgent**: 交通費精算専門エージェント
- **ReceiptExpenseAgent**: 領収書精算専門エージェント

各エージェントは独立してテスト可能ですが、統合テストでは連携動作も検証します。

### テスト実行時の注意

- テストは `output/` フォルダにファイルを生成しますが、テスト終了後に自動的に削除されます
- 一部のテストは実際のデータファイル（`data/train_fares.json`, `data/fixed_fares.json`）を使用します
- テスト実行前に、これらのファイルが存在することを確認してください

## テストデータ

テストで使用されるサンプルデータ：

```python
sample_routes = [
    {
        "departure": "渋谷",
        "destination": "東京",
        "date": "2025-01-15",
        "transport_type": "train",
        "cost": 200,
        "notes": ""
    },
    {
        "departure": "東京",
        "destination": "新宿",
        "date": "2025-01-15",
        "transport_type": "bus",
        "cost": 220,
        "notes": ""
    }
]
```

## トラブルシューティング

### テストが失敗する場合

1. **データファイルが見つからない**
   - `data/train_fares.json` と `data/fixed_fares.json` が存在するか確認

2. **モジュールが見つからない**
   - プロジェクトのルートディレクトリからテストを実行しているか確認
   - 必要なパッケージがインストールされているか確認

3. **SSL証明書エラー**
   - 企業プロキシ環境の場合、エージェントの初期化時にSSL検証が無効化されます

### テストの追加

新しいテストを追加する場合：

1. `tests/` ディレクトリに `test_*.py` ファイルを作成
2. テストクラスは `Test*` で始める
3. テスト関数は `test_*` で始める
4. `pytest` を実行して自動的に検出される

## CI/CD統合

GitHub ActionsやJenkinsなどのCI/CDパイプラインに統合する場合：

```yaml
# GitHub Actions の例
- name: Run tests
  run: |
    pip install pytest pytest-cov
    pytest --cov=agents --cov=tools --cov-report=xml
```

## 参考資料

- [pytest公式ドキュメント](https://docs.pytest.org/)
- [pytest-cov公式ドキュメント](https://pytest-cov.readthedocs.io/)
