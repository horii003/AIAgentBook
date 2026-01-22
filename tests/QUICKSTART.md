# テスト クイックスタートガイド

## 1. テスト環境のセットアップ

### 必要なパッケージのインストール

```bash
pip install pytest pytest-cov
```

または、requirements.txtから一括インストール：

```bash
pip install -r requirements.txt
```

## 2. テストの実行

### 基本的な実行

プロジェクトのルートディレクトリで以下を実行：

```bash
pytest
```

### 詳細な出力で実行

```bash
pytest -v
```

### 実行結果の例

```
============================================================ test session starts ============================================================
platform win32 -- Python 3.11.0, pytest-7.4.0
collected 33 items

tests/test_tools.py::TestFareTools::test_load_fare_data PASSED                                                                        [  3%]
tests/test_tools.py::TestFareTools::test_calculate_fare_train_valid PASSED                                                            [  6%]
tests/test_tools.py::TestFareTools::test_calculate_fare_train_invalid_route PASSED                                                    [  9%]
tests/test_tools.py::TestFareTools::test_calculate_fare_bus PASSED                                                                    [ 12%]
tests/test_tools.py::TestFareTools::test_calculate_fare_taxi PASSED                                                                   [ 15%]
tests/test_tools.py::TestFareTools::test_calculate_fare_airplane PASSED                                                               [ 18%]
tests/test_tools.py::TestFareTools::test_calculate_fare_invalid_transport PASSED                                                      [ 21%]
tests/test_tools.py::TestValidationTools::test_validate_date_valid PASSED                                                             [ 24%]
tests/test_tools.py::TestValidationTools::test_validate_date_invalid_format PASSED                                                    [ 27%]
tests/test_tools.py::TestValidationTools::test_validate_date_future PASSED                                                            [ 30%]
tests/test_tools.py::TestValidationTools::test_validate_location_valid PASSED                                                         [ 33%]
tests/test_tools.py::TestValidationTools::test_validate_location_empty PASSED                                                         [ 36%]
tests/test_tools.py::TestValidationTools::test_validate_amount_valid PASSED                                                           [ 39%]
tests/test_tools.py::TestValidationTools::test_validate_amount_negative PASSED                                                        [ 42%]
tests/test_tools.py::TestValidationTools::test_validate_amount_invalid PASSED                                                         [ 45%]
tests/test_tools.py::TestReportTools::test_generate_report_pdf PASSED                                                                 [ 48%]
tests/test_tools.py::TestReportTools::test_generate_report_json PASSED                                                                [ 51%]
tests/test_tools.py::TestReportTools::test_generate_report_empty_routes PASSED                                                        [ 54%]
tests/test_tools.py::TestReportTools::test_generate_report_invalid_format PASSED                                                      [ 57%]
tests/test_tools.py::TestReportTools::test_generate_report_missing_keys PASSED                                                        [ 60%]
tests/test_agent.py::TestTravelExpenseAgent::test_agent_initialization PASSED                                                         [ 63%]
tests/test_agent.py::TestTravelExpenseAgent::test_add_route PASSED                                                                    [ 66%]
tests/test_agent.py::TestTravelExpenseAgent::test_get_routes PASSED                                                                   [ 69%]
tests/test_agent.py::TestTravelExpenseAgent::test_clear_routes PASSED                                                                 [ 72%]
tests/test_agent.py::TestTravelExpenseAgent::test_agent_has_correct_tools PASSED                                                      [ 75%]
tests/test_agent.py::TestTravelExpenseAgent::test_agent_system_prompt PASSED                                                          [ 78%]
tests/test_integration.py::TestEndToEndWorkflow::test_complete_expense_report_workflow PASSED                                         [ 81%]
tests/test_integration.py::TestEndToEndWorkflow::test_multiple_transport_types PASSED                                                 [ 84%]
tests/test_integration.py::TestErrorHandling::test_invalid_route_handling PASSED                                                      [ 87%]
tests/test_integration.py::TestErrorHandling::test_invalid_format_handling PASSED                                                     [ 90%]
tests/test_integration.py::TestErrorHandling::test_empty_routes_handling PASSED                                                       [ 93%]

============================================================ 31 passed in 2.45s =============================================================
```

## 3. よく使うコマンド

### 特定のテストファイルのみ実行

```bash
# ツールのテストのみ
pytest tests/test_tools.py -v

# エージェントのテストのみ
pytest tests/test_agent.py -v

# 統合テストのみ
pytest tests/test_integration.py -v
```

### 特定のテストクラスのみ実行

```bash
pytest tests/test_tools.py::TestFareTools -v
```

### 特定のテスト関数のみ実行

```bash
pytest tests/test_tools.py::TestFareTools::test_calculate_fare_train_valid -v
```

### 失敗したテストのみ再実行

```bash
pytest --lf
```

### テストを途中で停止（最初の失敗で停止）

```bash
pytest -x
```

## 4. カバレッジレポートの生成

### HTMLレポートの生成

```bash
pytest --cov=agents --cov=tools --cov=handlers --cov-report=html
```

レポートは `htmlcov/index.html` に生成されます。ブラウザで開いて確認できます。

### ターミナルでカバレッジを確認

```bash
pytest --cov=agents --cov=tools --cov=handlers --cov-report=term-missing
```

## 5. トラブルシューティング

### エラー: ModuleNotFoundError

```
ModuleNotFoundError: No module named 'agents'
```

**解決策:** プロジェクトのルートディレクトリから実行してください。

```bash
cd C:\Users\scck-hidaka\Develop\travel_ver2
pytest
```

### エラー: データファイルが見つからない

```
FileNotFoundError: [Errno 2] No such file or directory: 'data/train_fares.json'
```

**解決策:** `data/` フォルダに必要なファイルが存在するか確認してください。

### エラー: SSL証明書エラー

企業プロキシ環境でSSL証明書エラーが発生する場合、エージェントの初期化時に自動的に対処されます。

## 6. 次のステップ

- 詳細なテストガイドは `tests/README.md` を参照
- 新しいテストを追加する場合は、既存のテストを参考にしてください
- CI/CD統合については `tests/README.md` の該当セクションを参照

## 7. よくある質問

**Q: テストはどのくらいの時間がかかりますか？**
A: 通常、すべてのテストは2〜5秒程度で完了します。

**Q: テストでファイルが生成されますか？**
A: はい、`output/` フォルダにPDFやJSONファイルが生成されますが、テスト終了後に自動的に削除されます。

**Q: AWS認証情報は必要ですか？**
A: ほとんどのテストは不要です。LLM呼び出しが必要なテストはスキップされています。

**Q: テストが失敗した場合はどうすればいいですか？**
A: エラーメッセージを確認し、該当するコードを修正してください。詳細は `-v` オプションで確認できます。
