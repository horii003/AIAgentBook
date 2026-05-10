---
inclusion: fileMatch
fileMatchPattern: "{.kiro/artifact-workflow/prompts/06_code-generation/**,artifacts/06_code-generation/src/**}"
---

# ディレクトリ構造ルール

## R1. ディレクトリ構造

Strandsマルチエージェントプロジェクトの標準ディレクトリ構造を以下に定義する。
`{project_root}/` はプロジェクトのルートディレクトリを表す。

```
{project_root}/
├── main.py                        # アプリケーションエントリーポイント
├── pyproject.toml                 # Python依存パッケージ定義・テスト設定（PEP 517/518）
├── README.md                      # プロジェクト概要・セットアップ手順
├── .env.template                  # 環境変数テンプレート
├── .gitignore                     # Git除外設定
├── config/                        # 設定管理
│   ├── __init__.py
│   ├── model_config.py            # LLMモデル設定
│   └── settings.py                # エージェント動作パラメータ（pydantic-settings）
├── models/                        # データモデル定義
│   ├── __init__.py
│   └── data_models.py             # Pydanticモデル定義
├── agents/                        # エージェント定義（オーケストレーター＋専門エージェント）
│   ├── __init__.py
│   ├── base_agent.py              # エージェント共通ユーティリティ（ファクトリ・呼び出しラッパー）
│   ├── orchestrator_agent.py      # オーケストレーターエージェント
│   ├── specialist_a_agent.py      # 専門エージェントA（業務ドメインに応じて命名）
│   └── specialist_b_agent.py      # 専門エージェントB（必要に応じて追加）
├── guardrails/                     # ガードレール
│   └── guardrails_cloudformation.yaml  # ガードレール作成用スクリプト
├── handlers/                      # 横断的関心事（エラー処理、フック）
│   ├── __init__.py
│   ├── error_handler.py           # エラーハンドリング・ログ出力
│   ├── loop_control_hook.py       # ReActループ制御フック
│   └── human_approval_hook.py     # Human-in-the-Loop承認フック
├── tools/                         # エージェントが利用するツール関数
│   ├── __init__.py
│   ├── {domain}_tools.py          # ドメイン固有のツール（検索、計算等）
│   └── output_generator.py        # 出力生成ツール（Excel、PDF等）
├── prompt/                        # 各エージェントのシステムプロンプト
│   ├── __init__.py
│   ├── prompt_orchestrator.py     # オーケストレーターのプロンプト
│   ├── prompt_specialist_a.py     # 専門エージェントAのプロンプト
│   └── prompt_specialist_b.py     # 専門エージェントBのプロンプト
├── knowledge/               # エージェントが参照するビジネスルール・ポリシー
│   ├── __init__.py
│   ├── {domain_a}_policies.py     # ドメインAのビジネスルール
│   └── {domain_b}_policies.py     # ドメインBのビジネスルール
├── session/                       # セッション管理（会話履歴の永続化）
│   ├── __init__.py
│   └── session_manager.py         # FileSessionManagerラッパー
├── storage/                       # 実行時生成：セッションデータの永続化先
│   ├── __init__.py
│   └── sessions/                  # セッションごとのサブディレクトリ（実行時生成）
├── data/                          # 静的データファイル（マスタデータ等）
│   └── {data_name}.json           # 参照データ（JSON形式）
├── template/                      # 出力生成に使用するテンプレートファイル
│   └── {template_name}.xlsx       # 申請書・帳票等のテンプレート（Excel等）
├── sample/                        # サンプルデータ（テスト・デモ用）
├── output/                        # 実行時生成：出力ファイルの保存先
├── logs/                          # 実行時生成：ログファイルの出力先
├── evals/                         # エージェント評価フレームワーク
│   ├── __init__.py
│   └── eval_{evaluation_name}.py  # 評価スクリプト
├── docs/                          # ドキュメント
└── tests/                         # テストコード
    ├── unit/                      # 単体テスト
    │   └── test_{module_name}.py
    └── integration/               # 結合テスト
        └── test_{feature_name}.py
```

### カスタマイズガイド

- `agents/` 配下の専門エージェントは業務ドメインに応じて追加・命名する
- `tools/` 配下のツールは業務要件に応じて追加する
- `knowledge/` 配下のポリシーファイルは業務ルールごとに追加する
- `data/` 配下のデータファイルは必要なマスタデータに応じて追加する
- `interfaces/` 配下のアダプターはUI種別（CLI/Web/Slack等）ごとに追加する

---

## R2. ファイル配置ルール

| コンポーネント種別 | 配置先 | ファイル命名規則 | 例 |
|:---|:---|:---|:---|
| エージェント定義 | `agents/` | `{機能名}_agent.py` | `orchestrator_agent.py`, `order_agent.py` |
| エージェント共通ユーティリティ | `agents/` | `base_agent.py` | `base_agent.py` |
| ツール関数 | `tools/` | `{機能名}_tools.py` または `{機能名}_generator.py` | `search_tools.py`, `report_generator.py` |
| データモデル | `models/` | `{対象}_models.py` | `data_models.py`, `order_models.py` |
| 設定クラス | `config/` | `{対象}_config.py` または `{対象}_settings.py` | `model_config.py`, `settings.py` |
| エラー処理・フック | `handlers/` | `{機能名}_handler.py` または `{機能名}_hook.py` | `error_handler.py`, `loop_control_hook.py` |
| システムプロンプト | `prompt/` | `prompt_{エージェント名}.py` | `prompt_orchestrator.py`, `prompt_order.py` |
| ビジネスルール | `knowledge/` | `{対象}_policies.py` | `order_policies.py`, `approval_policies.py` |
| セッション管理 | `session/` | `{機能名}_manager.py` | `session_manager.py` |
| 静的データ | `data/` | `{データ名}.json` | `master_data.json`, `config_data.json` |
| テンプレートファイル | `template/` | `{テンプレート名}.{拡張子}` | `申請書_template.xlsx`, `report_template.xlsx` |
| エントリーポイント | プロジェクトルート | `main.py` | `main.py` |
| パッケージ初期化 | 各ディレクトリ | `__init__.py` | `__init__.py` |

---

## R3. ファイル間の依存関係ルール

依存の方向は上位層から下位層への一方向とする。同一層間の参照は許可するが、下位層から上位層への参照は禁止する。

### 依存関係の方向

```
[上位層]
  agents/     → tools/, prompt/, handlers/, session/, config/, models/, knowledge/
  main.py     → agents/, handlers/, config/

[中間層]
  tools/      → models/, handlers/
  prompt/     → knowledge/
  session/    → （外部ライブラリのみ: strands.session）

[下位層]
  handlers/   → handlers/（同一層内参照: loop_control_hook → error_handler）
  config/     → （外部ライブラリのみ: strands.models, pydantic_settings）
  models/     → （標準ライブラリ + pydantic のみ）
  knowledge/  → （依存なし: 純粋なテキスト返却）
```

### 禁止される依存方向

- `models/` → `agents/`, `tools/`, `handlers/` への参照
- `config/` → `agents/`, `tools/` への参照
- `handlers/` → `agents/`, `tools/` への参照
- `tools/` → `agents/` への参照
- `knowledge/` → 他の全モジュールへの参照
- `interfaces/` → `agents/`, `handlers/`, `tools/` への参照

---

## R4. データファイルの配置ルール

| 分類 | 配置先 | 説明 |
|:---|:---|:---|
| 静的マスタデータ | `data/` | アプリケーション動作に必要な参照データ。JSON形式。 |
| テンプレートファイル | `template/` | 出力生成（Excel・PDF等）に使用するテンプレートファイル。ツールから参照する。 |
| サンプルデータ | `sample/` | テスト・デモ用のファイル。本番動作には不要。 |
| セッション永続化データ | `storage/sessions/` | 実行時に自動生成。セッションIDごとのサブディレクトリに格納。 |
| ログファイル | `logs/` | 実行時に自動生成。UTF-8エンコーディング。 |

---

## R5. 出力ファイルの配置ルール

| 出力種別 | 配置先 | ファイル命名規則 | 例 |
|:---|:---|:---|:---|
| 出力ファイル（Excel/PDF等） | `output/` | `{出力種別}_{YYYYMMDD_HHMMSS}.{拡張子}` | `報告書_20260210_143022.xlsx` |
| ログファイル（INFO以上） | `logs/` | `app.log` | `app.log` |
| ログファイル（ERROR以上） | `logs/` | `error.log` | `error.log` |
| セッションデータ | `storage/sessions/` | `session_{セッションID}/` | `session_20260210_143022_a1b2c3d4/` |
