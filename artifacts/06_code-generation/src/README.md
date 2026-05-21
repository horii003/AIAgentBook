# マルチAIエージェント経費精算申請システム

AWS Strands SDK を使用したマルチAIエージェントによる経費精算申請システムです。

## 概要

- **AG-001 申請受付窓口エージェント**: ユーザーの申請内容を受け付け、申請種別を判断して専門エージェントに振り分けます
- **AG-002 交通費精算申請エージェント**: 移動情報を収集し、交通費を自動計算して申請書を生成します
- **AG-003 経費精算申請エージェント**: 経費情報を収集し、経費精算申請書を生成します

## セットアップ

### 1. 依存パッケージのインストール

```bash
pip install -e ".[dev]"
```

### 2. 環境変数の設定

```bash
cp .env.template .env
```

`.env` ファイルを開き、以下の値を設定してください:

- `AWS_ACCESS_KEY_ID`: AWSアクセスキーID
- `AWS_SECRET_ACCESS_KEY`: AWSシークレットアクセスキー
- `AWS_DEFAULT_REGION`: AWSリージョン（例: `ap-northeast-1`）
- `GUARDRAIL_ID`: Amazon Bedrockガードレールのリソースid（任意）
- `GUARDRAIL_VERSION`: ガードレールバージョン（デフォルト: `DRAFT`）

### 3. ガードレールのデプロイ（任意）

```bash
aws cloudformation deploy \
  --template-file guardrails/guardrails_cloudformation.yaml \
  --stack-name ai-agent-guardrail
```

デプロイ後、出力された `GuardrailId` を `.env` の `GUARDRAIL_ID` に設定してください。

## 実行方法

```bash
python main.py
```

## テスト実行

```bash
# 単体テスト
pytest tests/unit/ -v

# 結合テスト
pytest tests/integration/ -v

# 全テスト
pytest tests/ -v
```

## ディレクトリ構造

```
src/
├── main.py                    # エントリーポイント
├── agents/                    # エージェント定義
├── config/                    # 設定管理
├── data/                      # 静的データ（運賃データ等）
├── guardrails/                # ガードレール設定
├── handlers/                  # エラーハンドリング・フック
├── knowledge/                 # 業務ルール・ポリシー
├── models/                    # データモデル
├── prompt/                    # システムプロンプト
├── session/                   # セッション管理
├── template/                  # 申請書テンプレート
└── tools/                     # ツール関数
```
