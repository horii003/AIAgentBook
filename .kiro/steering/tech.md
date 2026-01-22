# 技術スタック

## 開発環境
- OS: Windows
- シェル: PowerShell/CMD
- 言語: Python

## LLM
- Amazon Bedrock
- 認証: AWS CLI（認証情報はユーザーが入力）

## SDK
- AWS Strands: AIエージェント開発フレームワーク

## フレームワーク・ライブラリ
- AWS CLI: 認証情報の管理
- AWS Strands: マルチエージェントシステムの構築とオーケストレーション

## よく使うコマンド

### 依存関係のインストール
```bash
pip install awscli
pip install strands-agents
pip install strands-agents-tools strands-agents-builder
```

### AWS CLI設定
```bash
aws configure
```

### ビルド
```bash
# Pythonプロジェクトのため、ビルドは不要
```

### テスト
```bash
python -m pytest
# または
python -m unittest discover
```

### 実行
```bash
python main.py
```

## コーディング規約
- インデント: スペース4つ（PEP 8準拠）
- 命名規則: 
  - 変数・関数: snake_case
  - クラス: PascalCase
  - 定数: UPPER_SNAKE_CASE
- コメント: 日本語で記述
- Pythonスタイルガイド: PEP 8に準拠

## AWS Bedrock使用時の注意
- 認証情報は環境変数またはAWS CLIの設定から取得
- リージョンの指定を忘れずに
- APIコール時のエラーハンドリングを適切に実装

## 備考
- AWS Bedrockを使用するため、AWS認証情報の設定が必須
- 認証情報はユーザーが`aws configure`コマンドで設定
- AWS Strandsを使用してAIエージェントのワークフローを構築
- マルチエージェントシステムのオーケストレーションに対応
