# セッション管理ガイド

## 概要

Strands AgentsのFileSessionManagerを使用して、エージェントの会話履歴と状態を永続化しています。アプリケーション再起動後も会話を継続できます。

## 使用方法

### 基本的な使い方

```bash
python main.py
```

1. 申請者名を入力（例: 山田太郎）
2. セッションID `user_山田太郎` が自動生成
3. 会話履歴が自動保存される
4. 再起動後も同じ申請者名で会話を継続可能

### セッションのリセット

会話中に `reset` と入力すると、会話履歴と申請者情報がリセットされます。

## セッションの保存場所

```
storage/sessions/
└── session_user_{申請者名}/
    ├── session.json
    └── agents/
        ├── agent_reception_agent/
        ├── agent_travel_agent/
        └── agent_receipt_expense_agent/
            ├── agent.json
            └── messages/
                ├── message_0.json
                ├── message_1.json
                └── ...
```

## 実装の詳細

### SessionManagerFactory

`session/session_manager.py`でFileSessionManagerのインスタンスを作成します。

```python
from session.session_manager import SessionManagerFactory

session_manager = SessionManagerFactory.create_session_manager(session_id="user_123")
```

### 自動保存のタイミング

1. メッセージ追加時
2. エージェント実行完了時
3. エージェント状態更新時

### エージェントごとの設定

| エージェント | セッションID | 保存内容 |
|------------|------------|---------|
| Reception Agent | `user_{申請者名}` | 会話履歴、エージェント状態 |
| Travel Agent | 継承 | 移動情報、交通費、会話履歴 |
| Receipt Expense Agent | 継承 | 領収書情報、経費区分、会話履歴 |

## 変更されたファイル

### 新規作成
- `session/__init__.py`
- `session/session_manager.py`

### 変更
- `agents/reception_agent.py`: セッションID生成、SessionManager設定
- `agents/travel_agent.py`: session_idパラメータ追加、SessionManager統合
- `agents/receipt_expense_agent.py`: session_idパラメータ追加、SessionManager統合

## 注意事項

### セッションID
現在は申請者名から生成していますが、本番環境ではUUID等の使用を推奨します。

### クリーンアップ
古いセッションデータは手動で削除が必要です。定期的なクリーンアップを推奨します。

### スレッドセーフティ
SessionManagerはスレッドセーフではありません。マルチユーザー環境では各ユーザーに一意のセッションIDを割り当ててください。

## トラブルシューティング

### セッションが復元されない
1. セッションIDを確認
2. `storage/sessions/`ディレクトリの存在を確認
3. セッションファイルの破損を確認

### セッションファイルが大きい
- Conversation Managerの`window_size`を調整
- 定期的にセッションをリセット

## テスト

```bash
# すべてのセッション管理テストを実行
python -m pytest tests/test_session_manager.py -v -s

# 基本テストのみ実行
python -m pytest tests/test_session_basic.py -v -s
```

テスト結果の詳細は `tests/TEST_RESULTS_SESSION_MANAGER.md` を参照してください。

## 参考資料

- [Strands Agents Session Management](https://strandsagents.com/latest/documentation/docs/user-guide/concepts/agents/session-management/)
- [FileSessionManager API Reference](https://strandsagents.com/latest/documentation/docs/api-reference/python/session/file_session_manager/)
