# セッションID生成の共通化リファクタリング

## 概要

セッションID生成ロジックを`ReceptionAgent`から`SessionManagerFactory`に移動し、再利用性とテスト容易性を向上させました。

## 変更日

2026年2月9日

## 変更内容

### 1. `session/session_manager.py`

#### 追加されたメソッド

```python
@classmethod
def generate_session_id(cls, prefix: str = "") -> str:
    """
    一意のセッションIDを生成
    
    セッションIDはタイムスタンプ（秒単位）とUUID（8文字）の組み合わせで生成されます。
    これにより、同じ秒に複数のセッションが開始されても衝突を防ぎます。
    
    Args:
        prefix: セッションIDのプレフィックス（オプション）
               例: "test", "user_a" など
    
    Returns:
        str: 生成されたセッションID
            - prefixなし: "YYYYMMDD_HHMMSS_uuid8"
            - prefixあり: "prefix_YYYYMMDD_HHMMSS_uuid8"
    
    Examples:
        >>> SessionManagerFactory.generate_session_id()
        "20260209_143022_a1b2c3d4"
        
        >>> SessionManagerFactory.generate_session_id("test")
        "test_20260209_143022_a1b2c3d4"
    """
```

#### 追加されたインポート

```python
import uuid
from datetime import datetime
```

### 2. `agents/reception_agent.py`

#### 変更前

```python
import uuid
from datetime import datetime

# セッションIDをUUID + タイムスタンプで生成
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
unique_id = str(uuid.uuid4())[:8]
self._session_id = f"{timestamp}_{unique_id}"
```

#### 変更後

```python
from datetime import datetime  # uuidのインポートを削除

# セッションIDを生成（SessionManagerFactoryの共通メソッドを使用）
self._session_id = SessionManagerFactory.generate_session_id()
```

### 3. `tests/test_session_id_generation.py`（新規作成）

セッションID生成機能の単体テストを追加：

- `test_generate_session_id_without_prefix`: プレフィックスなしのID生成
- `test_generate_session_id_with_prefix`: プレフィックスありのID生成
- `test_generate_session_id_uniqueness`: 100個のIDの一意性確認
- `test_generate_session_id_with_various_prefixes`: 様々なプレフィックスでの生成

## 改善点

### 1. 再利用性の向上

- セッションID生成ロジックが`SessionManagerFactory`に集約されました
- 他のエージェントやモジュールから簡単に利用できます
- 将来的なAPI、CLI、Webインターフェースでも同じロジックを使用可能

### 2. テスト容易性の向上

- セッションID生成を独立してテスト可能
- プレフィックス付きIDの生成により、テスト用セッションの識別が容易
- モックやスタブを使用したテストが簡単に

### 3. 責任の分離

- セッション管理に関する機能が`SessionManagerFactory`に集約
- `ReceptionAgent`はエージェント固有の責務に集中

### 4. 一貫性の確保

- プロジェクト全体で統一されたセッションID形式
- 将来的な変更が一箇所で完結

## セッションIDの形式

### 基本形式（プレフィックスなし）

```
YYYYMMDD_HHMMSS_uuid8
```

例: `20260209_143022_a1b2c3d4`

### プレフィックス付き形式

```
prefix_YYYYMMDD_HHMMSS_uuid8
```

例: `test_20260209_143022_a1b2c3d4`

## 衝突リスク

- タイムスタンプ（秒単位）+ UUID（8文字）の組み合わせ
- UUID（8文字）の衝突確率: 約 1/4,294,967,296（約43億分の1）
- 同じ秒に複数のセッションが開始されても、UUIDで区別されます

## 使用例

### 基本的な使用

```python
from session.session_manager import SessionManagerFactory

# セッションIDを生成
session_id = SessionManagerFactory.generate_session_id()
print(session_id)  # 例: "20260209_143022_a1b2c3d4"

# セッションマネージャーを作成
session_manager = SessionManagerFactory.create_session_manager(session_id)
```

### テスト用セッションの作成

```python
# テスト用のプレフィックスを付けてセッションIDを生成
test_session_id = SessionManagerFactory.generate_session_id(prefix="test")
print(test_session_id)  # 例: "test_20260209_143022_a1b2c3d4"
```

### ユーザー別セッションの作成

```python
# ユーザー名をプレフィックスとして使用
user_session_id = SessionManagerFactory.generate_session_id(prefix="user_alice")
print(user_session_id)  # 例: "user_alice_20260209_143022_a1b2c3d4"
```

## テスト結果

```bash
$ python -m pytest tests/test_session_id_generation.py -v -s

tests/test_session_id_generation.py::TestSessionIDGeneration::test_generate_session_id_without_prefix PASSED
tests/test_session_id_generation.py::TestSessionIDGeneration::test_generate_session_id_with_prefix PASSED
tests/test_session_id_generation.py::TestSessionIDGeneration::test_generate_session_id_uniqueness PASSED
tests/test_session_id_generation.py::TestSessionIDGeneration::test_generate_session_id_with_various_prefixes PASSED

======================= 4 passed in 0.88s =======================
```

## 後方互換性

- 既存のセッションIDの形式は変更されていません
- 既存のセッションファイルは引き続き使用可能
- `ReceptionAgent`の動作に変更はありません

## 今後の拡張可能性

### 1. カスタムフォーマット

将来的に異なるフォーマットが必要な場合、`generate_session_id()`にフォーマット引数を追加可能：

```python
@classmethod
def generate_session_id(cls, prefix: str = "", format: str = "default") -> str:
    if format == "short":
        # 短縮形式
        return f"{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:4]}"
    # デフォルト形式
    ...
```

### 2. セッションIDの検証

セッションIDの形式を検証するメソッドの追加：

```python
@classmethod
def validate_session_id(cls, session_id: str) -> bool:
    """セッションIDの形式が正しいか検証"""
    parts = session_id.split("_")
    if len(parts) < 3:
        return False
    # 日付、時刻、UUIDの形式を検証
    ...
```

### 3. セッションIDからのメタデータ抽出

```python
@classmethod
def parse_session_id(cls, session_id: str) -> dict:
    """セッションIDからメタデータを抽出"""
    parts = session_id.split("_")
    return {
        "prefix": parts[0] if len(parts) == 4 else None,
        "date": parts[-3],
        "time": parts[-2],
        "uuid": parts[-1]
    }
```

## 関連ドキュメント

- [セッション管理ガイド](./session_management_guide.md)
- [エラーハンドリングベストプラクティス](./error_handling_best_practices.md)

## 変更履歴

| 日付 | 変更内容 | 担当者 |
|------|---------|--------|
| 2026-02-09 | セッションID生成の共通化リファクタリング | - |
