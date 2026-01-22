# プロジェクト構成

## ディレクトリ構造

```
travel_ver2/
├── .kiro/              # Kiro設定ファイル
│   └── steering/       # AIアシスタント用のステアリングルール
├── requirements.txt         # 依存パッケージ 
├── .env                     # 環境変数（APIキー等） 
├── main.py                  # エントリーポイント 
├── agents/ 
│   ├── __init__.py 
│   ├── base_agent.py       # 基本エージェント定義 
│   └── multi_agent.py      # マルチエージェント構成 
├── models/ 
│   ├── __init__.py 
│   └── provider_config.py  # モデルプロバイダー設定 
├── tools/ 
│   ├── __init__.py 
│   ├── custom_tools.py     # カスタムツール実装 
│   ├── api_tools.py        # API連携ツール 
│   └── data_tools.py       # データ処理ツール 
├── prompts/ 
│   ├── __init__.py 
│   ├── templates.py        # プロンプトテンプレート 
│   ├── system_prompts.py   # システムプロンプト 
│   └── examples.py         # Few-shot例 
├── handlers/ 
│   ├── __init__.py 
│   ├── error_handler.py    # エラーハンドリング 
│   ├── callback_handler.py # コールバック処理 
│   └── loop_handler.py     # エージェントループ制御 
├── storage/ 
│   ├── __init__.py 
│   ├── state_manager.py    # 状態管理 
│   └── memory.py          # メモリ管理 
├── context/ 
│   ├── __init__.py 
│   └── manager.py         # コンテキスト管理 
├── deployment/ 
│   ├── config.yaml        # デプロイメント設定  
|
|-- data                  #ローカルデータフォルダ
|--output                 #出力した申請書フォルダ


## フォルダの役割

### `.kiro/`
Kiro IDE の設定ファイルを格納するディレクトリ

### `.kiro/steering/`
AIアシスタントがプロジェクトを理解するためのガイドラインを格納

## ファイル命名規則
structure.mdを参照

## モジュール構成
未定（プロジェクト開発中）

## 備考
プロジェクトの構造が決まり次第、このドキュメントを更新してください。
具体的なフォルダ構成やファイル配置のルールを追加することをお勧めします。
