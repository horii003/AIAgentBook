# 会話管理（Conversation Management）ガイド

## 概要

このプロジェクトでは、Strands Agents SDKの`SlidingWindowConversationManager`を使用して、各エージェントの会話履歴を効率的に管理しています。

## SlidingWindowConversationManagerとは

会話履歴を固定数の最新メッセージに制限することで、以下の利点があります：

- **トークン制限の管理**: LLMのコンテキストウィンドウ制限内に収める
- **パフォーマンス最適化**: 処理時間とコストを削減
- **関連性の維持**: 最新の会話に集中
- **メモリ効率**: 不要な履歴を削除

## マルチエージェント構成における設定戦略

### 1. オーケストレーターエージェント（reception_agent）

```python
conversation_manager=SlidingWindowConversationManager(
    window_size=30,  # 大きめに設定
    should_truncate_results=True,
    per_turn=False
)
```

**理由:**
- 複数の専門エージェントとのやり取りを調整する必要がある
- ユーザーの元の要求と各専門エージェントの応答を追跡
- より長い会話コンテキストが必要

**推奨値:** 30-50メッセージ

### 2. 専門エージェント - 交通費精算（travel_agent）

```python
conversation_manager=SlidingWindowConversationManager(
    window_size=20,  # 中程度に設定
    should_truncate_results=True,
    per_turn=False
)
```

**理由:**
- 複数区間の移動情報を段階的に収集
- 各区間の確認と修正のやり取りが必要
- 最終的な申請書生成まで情報を保持

**推奨値:** 15-25メッセージ

### 3. 専門エージェント - 経費精算（receipt_expense_agent）

```python
conversation_manager=SlidingWindowConversationManager(
    window_size=15,  # 小さめに設定
    should_truncate_results=True,
    per_turn=False
)
```

**理由:**
- 単一の領収書処理に集中
- 比較的短い会話で完結
- 画像解析結果の確認と修正のみ

**推奨値:** 10-20メッセージ

## パラメータの詳細

### window_size

保持する最大メッセージ数。この数を超えると古いメッセージから削除されます。

**設定の考え方:**
- タスクの複雑さに応じて調整
- 長期的なコンテキストが必要な場合は大きく
- 単純なタスクは小さく

### should_truncate_results

ツール実行結果が大きすぎる場合に切り詰めるかどうか。

**推奨:** `True`（デフォルト）
- 大きな画像解析結果やExcel生成結果を自動的に要約
- コンテキストウィンドウの効率的な利用

### per_turn

各モデル呼び出し前にコンテキスト管理を適用するかどうか。

**設定オプション:**
- `False`（デフォルト）: エージェントループ完了後のみ適用
- `True`: 各モデル呼び出し前に適用
- `整数N`: N回のモデル呼び出しごとに適用

**推奨:** `False`
- 通常のユースケースでは十分
- `True`は長時間実行されるエージェントループで有用

## 実装のベストプラクティス

### 1. エージェントの役割に応じた設定

```python
# オーケストレーター: 大きめ
orchestrator_manager = SlidingWindowConversationManager(window_size=30)

# 複雑なタスク: 中程度
complex_task_manager = SlidingWindowConversationManager(window_size=20)

# シンプルなタスク: 小さめ
simple_task_manager = SlidingWindowConversationManager(window_size=15)
```

### 2. リセット機能の実装

各エージェントにリセット機能を実装し、新しい申請時に会話履歴をクリア：

```python
def reset_agent():
    global agent_instance
    agent_instance = None
```

### 3. モニタリング

会話履歴の使用状況を監視し、必要に応じて調整：

```python
# エージェントのメッセージ数を確認
message_count = len(agent.messages)
print(f"Current message count: {message_count}")
```

## トラブルシューティング

### 問題: コンテキストが不足している

**症状:** エージェントが以前の情報を忘れる

**解決策:**
- `window_size`を増やす
- 重要な情報をシステムプロンプトに含める

### 問題: トークン制限エラー

**症状:** "Context window overflow"エラー

**解決策:**
- `window_size`を減らす
- `should_truncate_results=True`を確認
- システムプロンプトを簡潔にする

### 問題: パフォーマンスが遅い

**症状:** 応答時間が長い

**解決策:**
- `window_size`を減らす
- 不要なツール結果を削除
- `per_turn=True`を検討（長時間実行の場合）

## 代替オプション

### NullConversationManager

会話履歴を管理しない（すべて保持）：

```python
from strands.agent.conversation_manager import NullConversationManager

agent = Agent(
    conversation_manager=NullConversationManager()
)
```

**使用ケース:**
- 短い会話のみ
- デバッグ時
- 完全な履歴が必要な場合

### SummarizingConversationManager

古いメッセージを要約して保持：

```python
from strands.agent.conversation_manager import SummarizingConversationManager

agent = Agent(
    conversation_manager=SummarizingConversationManager(
        summary_ratio=0.3,
        preserve_recent_messages=10
    )
)
```

**使用ケース:**
- 長期的なコンテキストが重要
- 過去の情報を参照する必要がある
- より高度な会話管理が必要

## まとめ

マルチエージェント構成では、各エージェントの役割に応じて`window_size`を調整することが重要です：

- **オーケストレーター**: 30+ メッセージ（全体の調整）
- **複雑な専門エージェント**: 15-25 メッセージ（段階的な情報収集）
- **シンプルな専門エージェント**: 10-20 メッセージ（単一タスク）

この設定により、効率的なメモリ使用とコスト削減を実現しながら、必要なコンテキストを維持できます。
