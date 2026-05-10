---
inclusion: fileMatch
fileMatchPattern: ".kiro/artifact-workflow/prompts/06_code-generation/**"
---

# コードレビューチェックリスト

コード生成後に必ずこのチェックリストを用いてセルフレビューを実施すること。
各項目は `[ ]` → `[x]` と記入して確認済みを明示する。

---

## CL-1. Strands SDK パターン

### CL-1.1 Agent() コンストラクタ

- [ ] `agent_id`（snake_case）を設定しているか
- [ ] `name`（日本語表示名）を設定しているか
- [ ] `description`（役割説明）を設定しているか
  - 専門エージェントの `description` は Agent as Tools で LLM への説明文になるため必須
- [ ] `callback_handler=None` を設定しているか（全エージェント共通）
- [ ] `SlidingWindowConversationManager` で `should_truncate_results=True, per_turn=False` を設定しているか
- [ ] `ModelRetryStrategy` を設定しているか
- [ ] `session_manager` を設定しているか
- [ ] 適切な `hooks` を設定しているか（R9.5.4 のフック構成表を参照）

### CL-1.2 @tool デコレータ

- [ ] `invocation_state` にアクセスするツールは `@tool(context=True)` を使用しているか
- [ ] アクセスしないツールは `@tool` のみか（不要な `context=True` はコンテキスト消費を増やす）
- [ ] `@tool(context=True)` を付けた関数の最後の引数は `tool_context: ToolContext` か

### CL-1.3 @tool の docstring（tool spec）

- [ ] `tool_context` 引数は docstring の `Args:` に**記述していない**か（LLM に見せない引数）
- [ ] `list` / `dict` 型の引数は各要素のフィールド名・型・必須/任意を docstring に展開しているか（R9.9.2 参照）
- [ ] `Args:` の説明が LLM がパラメータを正しく構築できる十分な情報量か

### CL-1.4 invocation_state の受け渡し

- [ ] オーケストレーターが `InvocationState` Pydantic モデルで `model_dump()` して渡しているか
- [ ] `InvocationState` クラスが `models/data_models.py` に定義されているか
- [ ] 子エージェントへは `session_id` を除いた必要フィールドのみ渡しているか（R9.6.6 参照）

### CL-1.5 HookProvider

- [ ] `register_hooks` で `registry.add_callback()` を使用しているか（`add_hook()` は存在しない）
- [ ] `BeforeToolCallEvent` のハンドラー内で対象ツールをフィルタリングしているか（全ツール呼び出しで発火するため必須）
- [ ] ツール呼び出しのキャンセルは `event.cancel_tool = "メッセージ"` で行っているか（`event.cancel()` は存在しない）
- [ ] 複数ハンドラーで同一の式が繰り返されている場合はヘルパーメソッドに抽出しているか（R9.8.6 参照）

---

## CL-2. コード品質

### CL-2.1 DRY 原則

- [ ] 同一の処理フロー（バリデーション → テンプレート確認 → 書き込み → 保存）が複数ツールで重複していないか
- [ ] 重複している場合は内部ヘルパー関数（`_generate_form` 等）に抽出しているか（R9.12.1 参照）
- [ ] JSON ファイル読み込みパターン（存在確認 → open → json.load → エラー処理）が重複している場合はヘルパーに抽出しているか

### CL-2.2 例外処理

- [ ] 複数の `except` 節で同一の処理を行っていないか（タプルまたは共通親クラスで統合する）（R9.1 参照）
- [ ] `except Exception` の前に、より特定的な例外クラスで別の処理が必要な場合のみ複数 `except` を使用しているか
- [ ] `LoopLimitError` → `Exception` の順でキャッチしているか（R9.1 参照）

### CL-2.3 Pydantic バリデーター

- [ ] `field_validator` で共通バリデーター関数をラムダで包んでいないか（`classmethod(validate_xxx)` を直接渡す）（R9.3.3 参照）
- [ ] 定義したバリデーターは実際にモデルフィールドに適用されているか

### CL-2.4 キャッシュ・遅延ロード

- [ ] モジュールレベルキャッシュの「未ロード」判定に空リスト/辞書（`not _data`）を使用していないか（R9.12.4 参照）
- [ ] 初期化済みフラグ（`_xxx_loaded: bool = False`）で管理しているか
- [ ] 毎回生成してよい理由がない場合、`@lru_cache(maxsize=1)` でインスタンスをキャッシュしているか

### CL-2.5 未使用コード・インポート

- [ ] インポートしたシンボルはすべてそのファイル内で使用されているか（R9.12.2 参照）
- [ ] 設定ファイルに定義したパラメータはすべてアプリケーションコードで使用されているか
- [ ] 定義したPydanticモデルはすべて対応するツール関数で使用されているか

### CL-2.6 エラー返却キー名

- [ ] ツール関数のエラー返却辞書のキー名が出力Pydanticモデルのフィールド名と一致しているか
  - 例: `TransportCalculatorOutput.error_message` → `{"error_message": ...}`（`message` は不可）

---

## CL-3. ディレクトリ・ファイル名規約

- [ ] `knowledge/`（正）になっているか（`agent_knowledge/` 等の独自名は不可）（R1, R2 参照）
- [ ] 静的マスタデータ（JSON等）は `data/` に配置しているか（`template/` 等は不可）（R4 参照）
- [ ] テンプレートファイル（Excel等）は `template/` に配置しているか
- [ ] 出力ファイルは `output/` に配置しているか
- [ ] ファイル名の命名規則に従っているか（R2 の表を参照）
- [ ] ディレクトリ構造が `00_rule_directory_structure.md`（R1）に準拠していること

---

## CL-4. 設定・環境変数

- [ ] `.env.template` に必要な環境変数がすべて記載されているか（R10.1 参照）
- [ ] ビジネスルール値（期限月数・金額閾値等）を `settings.py` で一元管理しているか（ハードコード禁止）（R9.12.3 参照）
- [ ] ポリシー関数（`get_xxx_policies()`）は設定値を引数で受け取り動的展開しているか（R9.12.3 参照）

---

## CL-5. ログ出力

- [ ] ログを出力するモジュールの先頭に `_logger = logging.getLogger(__name__)` があるか
- [ ] ログを出力しない薄いラッパーモジュールに `_logger` を定義していないか（R9.2 参照）
- [ ] `ErrorHandler` クラスのメソッド内でログ出力を行っていないか（ログは呼び出し元の責務）（R9.2 参照）
- [ ] エラー時の `_logger.error(...)` には `exc_info=True` を付与しているか（R9.2 参照）
