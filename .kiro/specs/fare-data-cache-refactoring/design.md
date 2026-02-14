# 設計ドキュメント

## 概要

本ドキュメントは、運賃データキャッシュ機構の改修に関する設計を定義します。現在の実装では、グローバル変数`_fare_data_cache`を使用して運賃データをキャッシュしていますが、これには以下の問題があります：

1. **スレッドセーフティの欠如**: 複数のスレッドから同時にアクセスされた場合、競合状態が発生する可能性
2. **テスト困難性**: グローバル状態がテスト間で永続化し、テストの独立性が損なわれる
3. **データ改ざんリスク**: グローバル変数は誰でも変更可能で、意図しない変更のリスクがある
4. **メモリ管理の困難さ**: キャッシュのクリアや更新が困難
5. **依存性の不透明さ**: 関数がグローバル状態に依存していることが明示的でない

本設計では、これらの問題を解決するために、2つの異なるキャッシュ戦略を実装可能な`FareDataManager`クラスを導入します。

## アーキテクチャ

### 全体構成

```
┌─────────────────────────────────────────┐
│         calculate_fare()                │
│      (AWS Strands @tool)                │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│       FareDataManager                   │
│  ┌───────────────────────────────────┐  │
│  │   CacheStrategy (抽象)            │  │
│  │  ┌─────────────┬──────────────┐   │  │
│  │  │ NoCacheStr. │ SingletonStr.│   │  │
│  │  └─────────────┴──────────────┘   │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│         ErrorHandler                    │
│  (既存のエラーハンドリング)              │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      JSONファイル                        │
│  - data/train_fares.json                │
│  - data/fixed_fares.json                │
└─────────────────────────────────────────┘
```

### 設計原則

1. **Strategy パターン**: キャッシュ戦略を交換可能にする
2. **依存性注入**: ErrorHandlerとファイルパスを外部から注入可能にする
3. **単一責任の原則**: データ読み込みとキャッシュ管理を分離
4. **インターフェース分離**: 各戦略は必要最小限のインターフェースのみを実装
5. **Open/Closed 原則**: 新しいキャッシュ戦略を追加する際に既存コードを変更しない

## コンポーネントとインターフェース

### 1. CacheStrategy（抽象基底クラス）

キャッシュ戦略の共通インターフェースを定義します。

```python
from abc import ABC, abstractmethod
from typing import Dict, Optional

class CacheStrategy(ABC):
    """キャッシュ戦略の抽象基底クラス"""
    
    @abstractmethod
    def get_data(self, loader_func: callable) -> Dict:
        """
        運賃データを取得する
        
        Args:
            loader_func: データを読み込む関数
            
        Returns:
            Dict: 運賃データ
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """キャッシュをクリアする（テスト用）"""
        pass
```

### 2. NoCacheStrategy（キャッシュなし戦略）

毎回ファイルから読み込む戦略です。

```python
class NoCacheStrategy(CacheStrategy):
    """キャッシュを使用せず、毎回ファイルから読み込む戦略"""
    
    def get_data(self, loader_func: callable) -> Dict:
        """毎回loader_funcを呼び出してデータを取得"""
        return loader_func()
    
    def clear(self) -> None:
        """キャッシュがないため何もしない"""
        pass
```

**特徴:**
- シンプルで理解しやすい
- スレッドセーフ（状態を持たない）
- テストが容易
- パフォーマンスは劣る（毎回ファイルI/O）

### 3. SingletonCacheStrategy（シングルトン戦略）

初回のみファイルから読み込み、以降はキャッシュから取得する戦略です。

```python
import threading
from typing import Dict, Optional

class SingletonCacheStrategy(CacheStrategy):
    """初回のみ読み込み、以降はキャッシュから取得する戦略"""
    
    def __init__(self):
        self._cache: Optional[Dict] = None
        self._lock = threading.Lock()
    
    def get_data(self, loader_func: callable) -> Dict:
        """
        Double-checked lockingパターンでスレッドセーフにキャッシュを管理
        """
        # 最初のチェック（ロックなし）
        if self._cache is not None:
            return self._cache
        
        # ロックを取得
        with self._lock:
            # 2回目のチェック（ロック内）
            if self._cache is None:
                self._cache = loader_func()
            return self._cache
    
    def clear(self) -> None:
        """キャッシュをクリアする（テスト用）"""
        with self._lock:
            self._cache = None
```

**特徴:**
- パフォーマンスが良い（初回のみファイルI/O）
- スレッドセーフ（Double-checked locking）
- メモリ効率的（1つのインスタンスのみ）
- 実装が複雑
- テスト時にキャッシュクリアが必要

### 4. FareDataManager（メインクラス）

運賃データの読み込みとキャッシュを管理するクラスです。

```python
import json
import os
from typing import Dict, Optional, Union
from pydantic import ValidationError
from models.data_models import FareData
from handlers.error_handler import ErrorHandler

class FareDataManager:
    """運賃データの読み込みとキャッシュを管理するクラス"""
    
    def __init__(
        self,
        strategy: Union[str, CacheStrategy] = "singleton",
        train_fares_path: str = "data/train_fares.json",
        fixed_fares_path: str = "data/fixed_fares.json",
        error_handler: Optional[ErrorHandler] = None
    ):
        """
        FareDataManagerの初期化
        
        Args:
            strategy: キャッシュ戦略（"no-cache", "singleton", または CacheStrategy インスタンス）
            train_fares_path: 電車運賃データのファイルパス
            fixed_fares_path: 固定運賃データのファイルパス
            error_handler: エラーハンドラー（Noneの場合は新規作成）
        
        Raises:
            ValueError: 無効な戦略名が指定された場合
        """
        self.train_fares_path = train_fares_path
        self.fixed_fares_path = fixed_fares_path
        self.error_handler = error_handler or ErrorHandler()
        
        # 戦略の設定
        if isinstance(strategy, str):
            self.strategy = self._create_strategy(strategy)
        else:
            self.strategy = strategy
    
    def _create_strategy(self, strategy_name: str) -> CacheStrategy:
        """文字列名から戦略インスタンスを作成"""
        strategies = {
            "no-cache": NoCacheStrategy,
            "singleton": SingletonCacheStrategy
        }
        
        if strategy_name not in strategies:
            raise ValueError(
                f"無効な戦略名: {strategy_name}. "
                f"有効な戦略: {', '.join(strategies.keys())}"
            )
        
        return strategies[strategy_name]()
    
    def get_fare_data(self) -> Dict:
        """
        運賃データを取得する
        
        Returns:
            Dict: {
                "train_fares": List[dict],
                "fixed_fares": dict
            }
        
        Raises:
            RuntimeError: データ読み込みに失敗した場合
        """
        return self.strategy.get_data(self._load_from_files)
    
    def _load_from_files(self) -> Dict:
        """ファイルから運賃データを読み込む（内部メソッド）"""
        # ファイルの存在確認
        self._check_file_exists(self.train_fares_path, "train_fares")
        self._check_file_exists(self.fixed_fares_path, "fixed_fares")
        
        try:
            # JSONファイルの読み込み
            with open(self.train_fares_path, "r", encoding="utf-8") as f:
                train_data = json.load(f)
            
            with open(self.fixed_fares_path, "r", encoding="utf-8") as f:
                fixed_data = json.load(f)
            
            # Pydanticモデルでバリデーション
            fare_data_model = FareData(
                train_fares=train_data.get("routes", []),
                fixed_fares=fixed_data
            )
            
            # ログ出力
            self.error_handler.log_info('運賃データを読み込みました')
            
            # 辞書形式で返す
            return {
                "train_fares": [route.model_dump() for route in fare_data_model.train_fares],
                "fixed_fares": fare_data_model.fixed_fares
            }
        
        except json.JSONDecodeError as e:
            error_msg = f"JSONファイルの解析に失敗しました: {e}"
            context = {
                "error_type": "JSONDecodeError",
                "train_fares_path": self.train_fares_path,
                "fixed_fares_path": self.fixed_fares_path
            }
            user_message = self.error_handler.handle_fare_data_error(
                ValueError(error_msg),
                context
            )
            raise RuntimeError(user_message)
        
        except ValidationError as e:
            error_msg = f"運賃データの形式が不正です: {e}"
            context = {"error_type": "ValidationError"}
            user_message = self.error_handler.handle_fare_data_error(
                ValueError(error_msg),
                context
            )
            raise RuntimeError(user_message)
        
        except Exception as e:
            error_msg = f"運賃データの読み込み中にエラーが発生しました: {e}"
            context = {"error_type": type(e).__name__}
            user_message = self.error_handler.handle_fare_data_error(
                ValueError(error_msg),
                context
            )
            raise RuntimeError(user_message)
    
    def _check_file_exists(self, file_path: str, file_type: str) -> None:
        """ファイルの存在を確認する"""
        if not os.path.exists(file_path):
            error_msg = f"運賃データファイルが見つかりません: {file_path}"
            context = {"file": file_path, "file_type": file_type}
            user_message = self.error_handler.handle_fare_data_error(
                FileNotFoundError(error_msg),
                context
            )
            raise RuntimeError(user_message)
    
    def clear_cache(self) -> None:
        """キャッシュをクリアする（テスト用）"""
        self.strategy.clear()
```

### 5. calculate_fare()の更新

既存の`calculate_fare()`関数を更新して、`FareDataManager`を使用するようにします。

```python
from strands import tool
from pydantic import ValidationError
from models.data_models import FareCalculationInput
from handlers.error_handler import ErrorHandler

# モジュールレベルでFareDataManagerのインスタンスを作成
# チュートリアル用途のため、シンプルなキャッシュなし戦略を使用
_fare_manager = FareDataManager(strategy="no-cache")
_error_handler = ErrorHandler()

@tool
def calculate_fare(
    departure: str,
    destination: str,
    transport_type: str,
    date: str
) -> dict:
    """
    経路の交通費を計算します。
    
    Args:
        departure: 出発地
        destination: 目的地
        transport_type: 交通手段（train/bus/taxi/airplane または 電車/バス/タクシー/飛行機）
        date: 移動日（YYYY-MM-DD形式）
    
    Returns:
        dict: {
            "fare": float,
            "calculation_method": str
        }
    """
    # 入力バリデーション
    try:
        input_data = FareCalculationInput(
            departure=departure,
            destination=destination,
            transport_type=transport_type,
            date=date
        )
    except ValidationError as e:
        # エラーハンドリング（既存と同じ）
        error_messages = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            error_messages.append(f"{field}: {error['msg']}")
        error_msg = f"入力データが不正です: {', '.join(error_messages)}"
        context = {
            "departure": departure,
            "destination": destination,
            "transport_type": transport_type,
            "date": date
        }
        user_message = _error_handler.handle_validation_error(
            ValueError(error_msg),
            context
        )
        raise RuntimeError(user_message)
    
    normalized_transport = input_data.transport_type
    
    # FareDataManagerから運賃データを取得
    fare_data = _fare_manager.get_fare_data()
    
    # 電車の場合
    if normalized_transport == "train":
        for route in fare_data["train_fares"]:
            if route["departure"] == departure and route["destination"] == destination:
                return {
                    "fare": float(route["fare"]),
                    "calculation_method": f"電車運賃テーブルから取得: {departure} → {destination}"
                }
        
        # 経路が見つからない場合
        error_msg = f"電車の運賃データに該当する経路が見つかりません: {departure} → {destination}"
        context = {
            "departure": departure,
            "destination": destination,
            "transport_type": normalized_transport,
            "date": date
        }
        user_message = _error_handler.handle_calculation_error(
            ValueError(error_msg),
            context
        )
        raise RuntimeError(user_message)
    
    # 固定運賃の場合
    else:
        fare = fare_data["fixed_fares"][normalized_transport]
        transport_name_map = {
            "bus": "バス",
            "taxi": "タクシー",
            "airplane": "飛行機"
        }
        return {
            "fare": float(fare),
            "calculation_method": f"{transport_name_map[normalized_transport]}の固定運賃"
        }
```

## データモデル

既存のPydanticモデルをそのまま使用します。変更は不要です。

- `TrainFareRoute`: 電車運賃の経路データ
- `FareData`: 運賃データ全体（train_fares + fixed_fares）
- `FareCalculationInput`: 運賃計算ツールの入力データ


## 2つのアプローチの詳細な比較

### アプローチ1: NoCacheStrategy（キャッシュなし）

#### 実装の詳細

```python
class NoCacheStrategy(CacheStrategy):
    """キャッシュを使用せず、毎回ファイルから読み込む戦略"""
    
    def get_data(self, loader_func: callable) -> Dict:
        """毎回loader_funcを呼び出してデータを取得"""
        return loader_func()
    
    def clear(self) -> None:
        """キャッシュがないため何もしない"""
        pass
```

#### メリット

1. **シンプルさ**: 実装が非常にシンプルで理解しやすい（わずか数行）
2. **スレッドセーフ**: 状態を持たないため、本質的にスレッドセーフ
3. **テスト容易性**: 各テストが独立しており、セットアップ/クリーンアップが不要
4. **メモリ効率**: データを保持しないため、メモリ使用量が最小
5. **データ鮮度**: 常に最新のファイル内容を読み込む
6. **デバッグ容易性**: 状態がないため、問題の切り分けが簡単

#### デメリット

1. **パフォーマンス**: 毎回ファイルI/Oが発生するため、呼び出しごとに数ミリ秒のオーバーヘッド
2. **ディスクI/O負荷**: 頻繁なファイルアクセスがディスクに負荷をかける
3. **スケーラビリティ**: 高頻度の呼び出しには不向き

#### パフォーマンス特性

- **初回呼び出し**: 約2-5ms（ファイル読み込み + JSON解析 + バリデーション）
- **2回目以降**: 約2-5ms（毎回同じ）
- **メモリ使用量**: 呼び出し中のみ一時的にメモリを使用
- **スレッド競合**: なし（状態を持たない）

#### 適用シナリオ

- 運賃データの更新頻度が高い場合
- 呼び出し頻度が低い場合（1分に数回程度）
- メモリ使用量を最小化したい場合
- 開発・デバッグ段階
- テスト環境

### アプローチ2: SingletonCacheStrategy（シングルトン）

#### 実装の詳細

```python
import threading
from typing import Dict, Optional

class SingletonCacheStrategy(CacheStrategy):
    """初回のみ読み込み、以降はキャッシュから取得する戦略"""
    
    def __init__(self):
        self._cache: Optional[Dict] = None
        self._lock = threading.Lock()
    
    def get_data(self, loader_func: callable) -> Dict:
        """Double-checked lockingパターンでスレッドセーフにキャッシュを管理"""
        # 最初のチェック（ロックなし）- 高速パス
        if self._cache is not None:
            return self._cache
        
        # ロックを取得して初期化
        with self._lock:
            # 2回目のチェック（ロック内）- 他のスレッドが初期化済みかチェック
            if self._cache is None:
                self._cache = loader_func()
            return self._cache
    
    def clear(self) -> None:
        """キャッシュをクリアする（テスト用）"""
        with self._lock:
            self._cache = None
```

#### メリット

1. **高パフォーマンス**: 2回目以降の呼び出しは数マイクロ秒で完了
2. **スケーラビリティ**: 高頻度の呼び出しに対応可能
3. **ディスクI/O削減**: 初回のみファイルアクセス
4. **本番環境向き**: 実運用に適したパフォーマンス特性
5. **メモリ効率**: 1つのインスタンスのみを保持

#### デメリット

1. **実装の複雑さ**: Double-checked lockingパターンが必要
2. **テストの複雑さ**: テスト間でキャッシュクリアが必要
3. **スレッド競合**: 初期化時にロック待ちが発生する可能性
4. **データ鮮度**: ファイルが更新されても反映されない（アプリ再起動が必要）
5. **デバッグ難易度**: 状態を持つため、問題の切り分けが複雑

#### パフォーマンス特性

- **初回呼び出し**: 約2-5ms（ファイル読み込み + JSON解析 + バリデーション）
- **2回目以降**: 約0.001-0.01ms（メモリアクセスのみ）
- **メモリ使用量**: 約10-50KB（運賃データのサイズに依存）
- **スレッド競合**: 初期化時のみロック（その後は読み取り専用）

#### Double-Checked Lockingの説明

```python
# 1. 最初のチェック（ロックなし）
if self._cache is not None:
    return self._cache  # 高速パス: ほとんどの呼び出しはここで終了

# 2. ロックを取得（初回のみ）
with self._lock:
    # 3. 2回目のチェック（ロック内）
    # 他のスレッドが既に初期化している可能性があるため再チェック
    if self._cache is None:
        self._cache = loader_func()  # 実際の初期化
    return self._cache
```

このパターンにより、以下を実現：
- 初期化は1回だけ（複数スレッドから同時呼び出しでも）
- 初期化後はロック不要（読み取り専用）
- 高いパフォーマンス

#### 適用シナリオ

- 運賃データの更新頻度が低い場合（日次または週次）
- 呼び出し頻度が高い場合（秒間数十回以上）
- パフォーマンスが重要な場合
- 本番環境
- 長時間稼働するアプリケーション

### 比較表

| 項目 | NoCacheStrategy | SingletonCacheStrategy |
|------|-----------------|------------------------|
| **実装の複雑さ** | ★☆☆☆☆（非常にシンプル） | ★★★☆☆（中程度） |
| **初回パフォーマンス** | 2-5ms | 2-5ms |
| **2回目以降パフォーマンス** | 2-5ms | 0.001-0.01ms（200-5000倍高速） |
| **メモリ使用量** | 最小（一時的のみ） | 10-50KB（常駐） |
| **スレッドセーフ** | ★★★★★（本質的） | ★★★★☆（実装に依存） |
| **テスト容易性** | ★★★★★（非常に簡単） | ★★★☆☆（クリーンアップ必要） |
| **データ鮮度** | ★★★★★（常に最新） | ★☆☆☆☆（再起動まで古い） |
| **スケーラビリティ** | ★★☆☆☆（低頻度向き） | ★★★★★（高頻度向き） |
| **デバッグ容易性** | ★★★★★（状態なし） | ★★★☆☆（状態あり） |
| **本番環境適性** | ★★☆☆☆（低負荷のみ） | ★★★★★（高負荷対応） |


### 推奨事項

**現在のプロジェクトに対する推奨**: **NoCacheStrategy（キャッシュなし戦略）**

理由：
1. **シンプルさ**: 書籍のチュートリアル用途のため、読者が理解しやすいコードが最優先
2. **ローカル環境**: ローカル環境での使用を想定しており、パフォーマンスよりも理解しやすさが重要
3. **複数人利用**: 複数人で同時に使用する可能性があり、スレッドセーフティが本質的に保証される
4. **デバッグ容易性**: 状態を持たないため、問題の切り分けが簡単
5. **教育目的**: 読者がコードを学習・改変しやすい

ただし、以下の場合はSingletonCacheStrategyを検討：
- 本番環境での大規模運用
- 高頻度の呼び出しが発生する場合（秒間数十回以上）
- パフォーマンスが重要な要件となる場合

**チュートリアルでの実装方針**:
- デフォルトでNoCacheStrategyを使用
- 設計ドキュメントでSingletonCacheStrategyについても説明し、読者が必要に応じて切り替えられるようにする
- 「発展的な内容」としてシングルトンパターンを紹介

### 戦略の切り替え方法

```python
# キャッシュなし戦略（デフォルト、チュートリアル推奨）
fare_manager = FareDataManager(strategy="no-cache")

# シングルトン戦略（発展的な内容、本番環境向け）
fare_manager = FareDataManager(strategy="singleton")

# カスタム戦略（拡張性）
custom_strategy = CustomCacheStrategy()
fare_manager = FareDataManager(strategy=custom_strategy)
```

**チュートリアルでの説明順序**:
1. まずNoCacheStrategyを実装・説明（メインコンテンツ）
2. 動作確認とテスト
3. 「発展的な内容」としてSingletonCacheStrategyを紹介
4. パフォーマンス比較を示す

## 正確性プロパティ

プロパティとは、すべての有効な実行において真であるべき特性や動作のことです。プロパティは、人間が読める仕様と機械で検証可能な正確性保証の橋渡しとなります。

### プロパティ1: データ読み込みの一貫性

*任意の*キャッシュ戦略において、同じファイルパスから複数回データを取得した場合、ファイルが変更されていない限り、同じデータ構造が返されること

**検証要件: 要件1.8**

### プロパティ2: スレッドセーフな初期化

*任意の*数のスレッドが同時にSingletonCacheStrategyのget_data()を呼び出した場合、loader_funcは正確に1回だけ実行されること

**検証要件: 要件3.2**

### プロパティ3: キャッシュクリア後の再読み込み

*任意の*キャッシュ戦略において、clear()を呼び出した後にget_data()を呼び出した場合、ファイルから新しくデータが読み込まれること

**検証要件: 要件4.3**

### プロパティ4: エラーハンドリングの一貫性

*任意の*ファイル読み込みエラー（FileNotFoundError、JSONDecodeError、ValidationError）において、FareDataManagerは適切なRuntimeErrorを発生させ、ErrorHandlerを通じてログに記録すること

**検証要件: 要件5.1, 5.2, 5.4**

### プロパティ5: 後方互換性

*任意の*有効な入力（departure, destination, transport_type, date）において、新しいcalculate_fare()は既存の実装と同じ結果を返すこと

**検証要件: 要件8.4**


### プロパティ6: NoCacheStrategyのステートレス性

*任意の*呼び出しシーケンスにおいて、NoCacheStrategyは内部状態を持たず、各get_data()呼び出しは独立していること

**検証要件: 要件3.4**

### プロパティ7: メモリ効率性

*任意の*キャッシュ戦略において、SingletonCacheStrategyは運賃データのコピーを1つだけ保持し、NoCacheStrategyは呼び出し後にデータを保持しないこと

**検証要件: 要件10.1, 10.2**

### プロパティ8: 戦略の交換可能性

*任意の*有効な戦略名（"no-cache", "singleton"）またはCacheStrategyインスタンスにおいて、FareDataManagerは正しく初期化され、同じインターフェースで動作すること

**検証要件: 要件9.1, 9.2, 9.3**

### プロパティ9: ファイルハンドルの解放

*任意の*データ読み込み操作において、成功・失敗に関わらず、ファイルハンドルは適切に閉じられること

**検証要件: 要件10.4**

### プロパティ10: Pydanticバリデーションの保持

*任意の*運賃データにおいて、FareDataManagerはTrainFareRouteとFareDataのPydanticモデルを使用してバリデーションを実行し、不正なデータを拒否すること

**検証要件: 要件1.6, 1.7**

## エラーハンドリング

### エラーの種類と処理

1. **FileNotFoundError**: 運賃データファイルが存在しない
   - ErrorHandler.handle_fare_data_error()を使用
   - ユーザーにファイルの場所を確認するよう促す
   - RuntimeErrorとして再送出

2. **JSONDecodeError**: JSONファイルの構文エラー
   - ErrorHandler.handle_fare_data_error()を使用
   - ファイル形式の確認を促す
   - RuntimeErrorとして再送出

3. **ValidationError**: Pydanticバリデーション失敗
   - ErrorHandler.handle_fare_data_error()を使用
   - データ形式の詳細なエラーメッセージを提供
   - RuntimeErrorとして再送出

4. **ValueError**: 無効な戦略名
   - 有効な戦略のリストを含むエラーメッセージ
   - 直接ValueErrorとして送出

### エラーログの記録

すべてのエラーは以下の情報とともにログに記録されます：
- エラータイプ
- エラーメッセージ
- コンテキスト情報（ファイルパス、入力値など）
- タイムスタンプ（ErrorHandlerが自動付与）


## テスト戦略

### デュアルテストアプローチ

本プロジェクトでは、ユニットテストとプロパティベーステストの両方を使用します。これらは相補的であり、包括的なカバレッジを実現します。

- **ユニットテスト**: 特定の例、エッジケース、エラー条件を検証
- **プロパティテスト**: すべての入力にわたる普遍的なプロパティを検証

### ユニットテスト

#### NoCacheStrategyのテスト

```python
import unittest
from tools.fare_cache import NoCacheStrategy

class TestNoCacheStrategy(unittest.TestCase):
    
    def test_get_data_calls_loader_every_time(self):
        """毎回loader_funcが呼ばれることを確認"""
        strategy = NoCacheStrategy()
        call_count = 0
        
        def mock_loader():
            nonlocal call_count
            call_count += 1
            return {"data": f"call_{call_count}"}
        
        result1 = strategy.get_data(mock_loader)
        result2 = strategy.get_data(mock_loader)
        
        self.assertEqual(call_count, 2)
        self.assertEqual(result1["data"], "call_1")
        self.assertEqual(result2["data"], "call_2")
    
    def test_clear_does_nothing(self):
        """clearが何もしないことを確認"""
        strategy = NoCacheStrategy()
        strategy.clear()  # エラーが発生しないことを確認
```

#### SingletonCacheStrategyのテスト

```python
import unittest
import threading
from tools.fare_cache import SingletonCacheStrategy

class TestSingletonCacheStrategy(unittest.TestCase):
    
    def setUp(self):
        """各テスト前にキャッシュをクリア"""
        self.strategy = SingletonCacheStrategy()
        self.strategy.clear()
    
    def test_get_data_caches_result(self):
        """初回のみloader_funcが呼ばれることを確認"""
        call_count = 0
        
        def mock_loader():
            nonlocal call_count
            call_count += 1
            return {"data": "cached"}
        
        result1 = self.strategy.get_data(mock_loader)
        result2 = self.strategy.get_data(mock_loader)
        
        self.assertEqual(call_count, 1)
        self.assertEqual(result1, result2)
    
    def test_clear_invalidates_cache(self):
        """clearがキャッシュを無効化することを確認"""
        call_count = 0
        
        def mock_loader():
            nonlocal call_count
            call_count += 1
            return {"data": f"call_{call_count}"}
        
        result1 = self.strategy.get_data(mock_loader)
        self.strategy.clear()
        result2 = self.strategy.get_data(mock_loader)
        
        self.assertEqual(call_count, 2)
        self.assertNotEqual(result1, result2)
    
    def test_thread_safety(self):
        """複数スレッドから同時アクセスしても1回だけ初期化されることを確認"""
        call_count = 0
        lock = threading.Lock()
        
        def mock_loader():
            nonlocal call_count
            with lock:
                call_count += 1
            return {"data": "thread_safe"}
        
        threads = []
        for _ in range(10):
            t = threading.Thread(target=lambda: self.strategy.get_data(mock_loader))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(call_count, 1)
```


#### FareDataManagerのテスト

```python
import unittest
import tempfile
import json
import os
from tools.fare_cache import FareDataManager

class TestFareDataManager(unittest.TestCase):
    
    def setUp(self):
        """テスト用の一時ファイルを作成"""
        self.temp_dir = tempfile.mkdtemp()
        
        # テスト用の運賃データ
        self.train_data = {
            "routes": [
                {"departure": "東京", "destination": "新宿", "fare": 200}
            ]
        }
        self.fixed_data = {
            "bus": 220,
            "taxi": 2000,
            "airplane": 50000
        }
        
        # ファイルに書き込み
        self.train_path = os.path.join(self.temp_dir, "train_fares.json")
        self.fixed_path = os.path.join(self.temp_dir, "fixed_fares.json")
        
        with open(self.train_path, "w", encoding="utf-8") as f:
            json.dump(self.train_data, f)
        
        with open(self.fixed_path, "w", encoding="utf-8") as f:
            json.dump(self.fixed_data, f)
    
    def tearDown(self):
        """一時ファイルを削除"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_load_data_successfully(self):
        """正常にデータを読み込めることを確認"""
        manager = FareDataManager(
            strategy="no-cache",
            train_fares_path=self.train_path,
            fixed_fares_path=self.fixed_path
        )
        
        data = manager.get_fare_data()
        
        self.assertIn("train_fares", data)
        self.assertIn("fixed_fares", data)
        self.assertEqual(len(data["train_fares"]), 1)
        self.assertEqual(data["fixed_fares"]["bus"], 220)
    
    def test_file_not_found_error(self):
        """ファイルが存在しない場合のエラーを確認"""
        manager = FareDataManager(
            strategy="no-cache",
            train_fares_path="nonexistent.json",
            fixed_fares_path=self.fixed_path
        )
        
        with self.assertRaises(RuntimeError) as context:
            manager.get_fare_data()
        
        self.assertIn("見つかりません", str(context.exception))
    
    def test_invalid_strategy_name(self):
        """無効な戦略名でエラーが発生することを確認"""
        with self.assertRaises(ValueError) as context:
            FareDataManager(strategy="invalid-strategy")
        
        self.assertIn("無効な戦略名", str(context.exception))
```

### プロパティベーステスト

Pythonでは`hypothesis`ライブラリを使用してプロパティベーステストを実装します。各テストは最低100回の反復を実行します。

#### インストール

```bash
pip install hypothesis
```

#### プロパティテストの実装

```python
from hypothesis import given, strategies as st, settings
import threading

class TestCacheStrategyProperties(unittest.TestCase):
    
    @given(st.integers(min_value=1, max_value=100))
    @settings(max_examples=100)
    def test_property_nocache_always_calls_loader(self, num_calls):
        """
        プロパティ6: NoCacheStrategyのステートレス性
        Feature: fare-data-cache-refactoring, Property 6: 
        任意の呼び出しシーケンスにおいて、NoCacheStrategyは各get_data()呼び出しで
        loader_funcを実行すること
        """
        strategy = NoCacheStrategy()
        call_count = 0
        
        def counter_loader():
            nonlocal call_count
            call_count += 1
            return {"count": call_count}
        
        for _ in range(num_calls):
            strategy.get_data(counter_loader)
        
        self.assertEqual(call_count, num_calls)
    
    @given(st.integers(min_value=1, max_value=50))
    @settings(max_examples=100)
    def test_property_singleton_calls_loader_once(self, num_threads):
        """
        プロパティ2: スレッドセーフな初期化
        Feature: fare-data-cache-refactoring, Property 2:
        任意の数のスレッドが同時にSingletonCacheStrategyのget_data()を呼び出した場合、
        loader_funcは正確に1回だけ実行されること
        """
        strategy = SingletonCacheStrategy()
        call_count = 0
        lock = threading.Lock()
        
        def thread_safe_loader():
            nonlocal call_count
            with lock:
                call_count += 1
            return {"data": "singleton"}
        
        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=lambda: strategy.get_data(thread_safe_loader))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        self.assertEqual(call_count, 1)
    
    @given(st.sampled_from(["no-cache", "singleton"]))
    @settings(max_examples=100)
    def test_property_cache_clear_forces_reload(self, strategy_name):
        """
        プロパティ3: キャッシュクリア後の再読み込み
        Feature: fare-data-cache-refactoring, Property 3:
        任意のキャッシュ戦略において、clear()を呼び出した後にget_data()を呼び出した場合、
        新しくデータが読み込まれること
        """
        if strategy_name == "no-cache":
            strategy = NoCacheStrategy()
        else:
            strategy = SingletonCacheStrategy()
        
        call_count = 0
        
        def counting_loader():
            nonlocal call_count
            call_count += 1
            return {"count": call_count}
        
        # 初回呼び出し
        result1 = strategy.get_data(counting_loader)
        initial_count = call_count
        
        # キャッシュクリア
        strategy.clear()
        
        # 再呼び出し
        result2 = strategy.get_data(counting_loader)
        
        # NoCacheは毎回呼ぶので、Singletonの場合のみチェック
        if strategy_name == "singleton":
            self.assertGreater(call_count, initial_count)
            self.assertNotEqual(result1["count"], result2["count"])
```

### テスト実行

```bash
# すべてのテストを実行
python -m pytest tests/

# 特定のテストファイルを実行
python -m pytest tests/test_fare_cache.py

# プロパティテストのみ実行
python -m pytest tests/test_fare_cache.py -k property
```

### テストカバレッジ目標

- ユニットテスト: 各クラス・メソッドの具体的な動作を検証
- プロパティテスト: 普遍的な性質を検証（最低100回の反復）
- カバレッジ目標: 90%以上

## 移行計画

### フェーズ1: 新しいコンポーネントの実装

1. `tools/fare_cache.py`を作成
   - CacheStrategy抽象クラス
   - NoCacheStrategy
   - SingletonCacheStrategy
   - FareDataManager

### フェーズ2: 既存コードの更新

1. `tools/fare_tools.py`を更新
   - グローバル変数`_fare_data_cache`を削除
   - `load_fare_data()`関数を削除
   - `calculate_fare()`を更新してFareDataManagerを使用

### フェーズ3: テストの実装

1. ユニットテストの作成
2. プロパティテストの作成
3. 統合テストの実行

### フェーズ4: 検証とデプロイ

1. すべてのテストが通ることを確認
2. 既存のエージェントコードが正常に動作することを確認
3. パフォーマンステストの実行
4. 本番環境へのデプロイ

## パフォーマンス考慮事項

### ベンチマーク

```python
import time

def benchmark_strategy(strategy, num_calls=1000):
    """戦略のパフォーマンスをベンチマーク"""
    def mock_loader():
        return {"data": "test"}
    
    start = time.time()
    for _ in range(num_calls):
        strategy.get_data(mock_loader)
    end = time.time()
    
    return end - start

# 実行例
no_cache = NoCacheStrategy()
singleton = SingletonCacheStrategy()

print(f"NoCacheStrategy: {benchmark_strategy(no_cache):.4f}秒")
print(f"SingletonCacheStrategy: {benchmark_strategy(singleton):.4f}秒")
```

### 期待される結果

- NoCacheStrategy: 約2-5秒（1000回の呼び出し）
- SingletonCacheStrategy: 約0.01-0.05秒（1000回の呼び出し）

パフォーマンス差: 約100-500倍

## セキュリティ考慮事項

1. **ファイルパスの検証**: 
   - ファイルパスはdata/ディレクトリ内に制限
   - パストラバーサル攻撃を防ぐ

2. **データバリデーション**:
   - Pydanticモデルによる厳格なバリデーション
   - 不正なデータの拒否

3. **エラーメッセージ**:
   - 機密情報を含まない
   - ユーザーフレンドリーなメッセージ

## まとめ

本設計では、グローバル変数を使用した現在のキャッシュ実装を、Strategyパターンを使用した柔軟で保守性の高い設計に改修します。2つの異なるキャッシュ戦略（NoCacheStrategyとSingletonCacheStrategy）を提供し、ユースケースに応じて選択できるようにします。

主な改善点：
- スレッドセーフティの確保
- テスタビリティの向上
- 依存性の明示化
- メモリ管理の改善
- 柔軟な戦略選択

推奨戦略：本番環境ではSingletonCacheStrategy、開発・テスト環境ではNoCacheStrategyを使用。


## チュートリアル向けの補足

### 学習の進め方

1. **ステップ1: 問題の理解**
   - 現在のグローバル変数の問題点を説明
   - なぜリファクタリングが必要かを理解

2. **ステップ2: シンプルな解決策（NoCacheStrategy）**
   - まずキャッシュなし戦略を実装
   - 動作確認とテスト
   - グローバル変数の問題が解決されたことを確認

3. **ステップ3: 発展的な内容（SingletonCacheStrategy）**
   - パフォーマンスの問題を提起
   - シングルトンパターンの説明
   - 実装とベンチマーク

4. **ステップ4: 設計パターンの理解**
   - Strategyパターンの説明
   - 拡張性の利点を理解

### コードの段階的な実装

**最初の実装（チュートリアルのメイン）**:
```python
# 最もシンプルな実装
class FareDataManager:
    def __init__(self, train_fares_path="data/train_fares.json", 
                 fixed_fares_path="data/fixed_fares.json"):
        self.train_fares_path = train_fares_path
        self.fixed_fares_path = fixed_fares_path
        self.error_handler = ErrorHandler()
    
    def get_fare_data(self):
        """毎回ファイルから読み込む（シンプル）"""
        return self._load_from_files()
    
    def _load_from_files(self):
        # ファイル読み込みロジック
        pass
```

**発展的な実装（オプション）**:
- Strategyパターンの導入
- SingletonCacheStrategyの追加
- パフォーマンス比較

### 読者へのメッセージ

「このチュートリアルでは、まずシンプルで理解しやすいキャッシュなし戦略を実装します。これにより、グローバル変数の問題を解決し、テストしやすいコードを作成できます。パフォーマンスが重要になった場合は、後からシングルトン戦略に切り替えることができます。」
