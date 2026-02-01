# エラーハンドリングガイド

## 概要

このドキュメントでは、エンドユーザー向けアプリケーションとしてのエラーハンドリング戦略について説明します。

## 基本方針

### エンドユーザー向けアプリケーションのエラーハンドリング

**原則**: すべてのエラーをキャッチして、ユーザーフレンドリーなメッセージに変換する

**理由**:
- ユーザーは技術的な詳細を知る必要がない
- スタックトレースはユーザーを混乱させる
- 開発者はログファイルで詳細を確認できる

## 実装内容

### 1. main.pyでのエラーハンドリング

すべてのエラーをキャッチして、適切なメッセージに変換します。

```python
try:
    agent.run()
except KeyboardInterrupt:
    # ユーザーによる中断
    print("\n\nシステムを終了します。")
    sys.exit(0)

except RuntimeError as e:
    # ループ制限エラー
    if "エージェントループの制限" in str(e):
        print("【処理が複雑すぎます】")
        print("もう一度、シンプルな内容でお試しください。")
    else:
        print("【エラー】")
        print("システムを再起動してください。")

except FileNotFoundError as e:
    # ファイルエラー
    print("【ファイルエラー】")
    print("必要なファイルが見つかりません。")

except PermissionError as e:
    # 権限エラー
    print("【権限エラー】")
    print("ファイルへのアクセス権限がありません。")

except ConnectionError as e:
    # 接続エラー
    print("【接続エラー】")
    print("Amazon Bedrockサービスへの接続に失敗しました。")

except ValueError as e:
    # 入力エラー
    print("【入力エラー】")
    print("入力データに問題があります。")

except Exception as e:
    # その他のすべてのエラー
    print("【予期しないエラー】")
    print("システムを再起動してください。")
```

### 2. reception_agentでのエラーハンドリング

対話ループ内でのエラーをキャッチして、ユーザーに分かりやすいメッセージを表示します。

```python
try:
    response = self.agent(user_input, invocation_state={...})
    print(f"\nエージェント: {response}")

except RuntimeError as e:
    if "エージェントループの制限" in str(e):
        print("【処理が複雑すぎます】")
        print("もう一度、シンプルな内容でお試しください。")
        # ログには詳細を記録
        logger.error(f"ループ制限エラー: {e}", exc_info=True)
    else:
        print("エラーが発生しました。もう一度お試しください。")
        logger.error(f"予期しないRuntimeError: {e}", exc_info=True)

except Exception as e:
    print("エラーが発生しました。もう一度お試しください。")
    logger.error(f"予期しないエラー: {e}", exc_info=True)
```

### 3. 専門エージェント（Agent as Tools）でのエラーハンドリング

専門エージェントでエラーが発生した場合、オーケストレーターに適切なメッセージを返します。

```python
try:
    response = agent(query, invocation_state={...})
    return str(response)

except RuntimeError as e:
    if "エージェントループの制限" in str(e):
        return (
            "申し訳ございません。処理が複雑すぎて完了できませんでした。\n\n"
            "受付窓口に戻りますので、もう一度シンプルな内容でお試しください。"
        )
    else:
        return "エラーが発生しました。受付窓口に戻ります。"

except Exception as e:
    logger.error(f"[travel_agent] エラーが発生しました: {e}")
    return "エラーが発生しました。受付窓口に戻ります。"
```

## ログ記録

### ユーザーへの表示とログの分離

- **ユーザーへの表示**: 分かりやすいメッセージのみ
- **ログファイル**: 詳細なエラー情報（スタックトレース含む）

```python
# ユーザーには分かりやすいメッセージ
print("【エラー】")
print("システムを再起動してください。")

# ログには詳細を記録（デバッグ用）
error_handler.log_error("RuntimeError", str(e), {"error_type": "RuntimeError"}, exc_info=True)
```

### ログレベルの設定

```python
# スタックトレースを抑制（エンドユーザー向けアプリケーション）
logging.getLogger("strands.event_loop.event_loop").setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore")
```

## エラーメッセージの設計

### ユーザーフレンドリーなメッセージの原則

1. **明確な見出し**: 【処理が複雑すぎます】【ファイルエラー】など
2. **状況の説明**: 何が起こったかを簡潔に説明
3. **対処方法**: ユーザーが取るべき行動を具体的に提示
4. **サポート情報**: 問題が解決しない場合の連絡先

### 良い例

```
============================================================
【処理が複雑すぎます】
============================================================

申し訳ございません。処理が複雑すぎて完了できませんでした。

以下のいずれかをお試しください：
1. タスクをより小さな単位に分割してください
   例：複数の申請を一度に行う場合は、1つずつ申請してください
2. より具体的な指示を提供してください
   例：「交通費を申請したい」→「1月10日の東京から大阪への新幹線代を申請したい」
3. 不要な情報を削除してください
   例：申請に関係のない質問や情報は別途お尋ねください
============================================================
もう一度、シンプルな内容でお試しください。
============================================================
```

### 悪い例（技術的すぎる）

```
RuntimeError: エージェントループの制限に到達しました（15回）。
Traceback (most recent call last):
  File "...", line 107, in on_after_model_call
    raise RuntimeError(error_message)
```

## エラーの種類と対応

| エラータイプ | ユーザーメッセージ | ログ記録 | システム終了 |
|------------|------------------|---------|------------|
| KeyboardInterrupt | システムを終了します | INFO | Yes (0) |
| RuntimeError (ループ制限) | 処理が複雑すぎます | ERROR (exc_info=True) | Yes (1) |
| RuntimeError (その他) | 予期しないエラー | ERROR (exc_info=True) | Yes (1) |
| FileNotFoundError | ファイルエラー | ERROR (exc_info=True) | Yes (1) |
| PermissionError | 権限エラー | ERROR (exc_info=True) | Yes (1) |
| ConnectionError | 接続エラー | ERROR (exc_info=True) | Yes (1) |
| ValueError | 入力エラー | ERROR (exc_info=True) | Yes (1) |
| Exception (その他) | 予期しないエラー | ERROR (exc_info=True) | Yes (1) |

## デバッグ時の対応

開発中にスタックトレースを確認したい場合は、ログファイル（`logs/error.log`）を確認してください。

```bash
# ログファイルの確認
type logs\error.log

# リアルタイムでログを監視（PowerShell）
Get-Content logs\error.log -Wait -Tail 10
```

## まとめ

- エンドユーザー向けアプリケーションでは、すべてのエラーをキャッチして適切なメッセージに変換する
- ユーザーには分かりやすいメッセージのみを表示
- 開発者はログファイルで詳細を確認
- スタックトレースはログファイルにのみ記録
