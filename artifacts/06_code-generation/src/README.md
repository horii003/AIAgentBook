# 経費精算申請マルチエージェントシステム

社員の交通費精算申請・経費精算申請をAIエージェントがサポートするシステムです。

## セットアップ

```bash
# 依存パッケージのインストール
pip install -e ".[dev]"

# 環境変数の設定
cp .env.template .env
# .envを編集してAWS認証情報・ガードレールIDを設定する
```

## 実行

```bash
python main.py
```

## テスト

```bash
pytest tests/ -v
```

## ディレクトリ構造

```
src/
├── main.py                    # エントリーポイント
├── config/                    # 設定管理
├── models/                    # データモデル
├── agents/                    # エージェント定義
├── handlers/                  # エラー処理・フック
├── tools/                     # ツール関数
├── prompt/                    # システムプロンプト
├── knowledge/                 # ビジネスルール
├── session/                   # セッション管理
├── data/                      # 静的データファイル
├── template/                  # Excelテンプレート
├── guardrails/                # ガードレール設定
└── tests/                     # テストコード
```
