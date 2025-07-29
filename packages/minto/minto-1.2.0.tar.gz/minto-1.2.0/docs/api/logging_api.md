# ログ機能 API リファレンス

## モジュール概要

Mintoライブラリのログ機能は以下のモジュールで構成されています：

- `minto.logging_config`: ログ設定とフォーマット機能
- `minto.logger`: メインログインターフェース

## minto.logging_config

### LogLevel

ログレベルを定義する列挙型です。

```python
class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
```

**使用例:**
```python
from minto.logging_config import LogLevel
config = LogConfig(level=LogLevel.DEBUG)
```

### LogFormat

ログフォーマットを定義する列挙型です。

```python
class LogFormat(Enum):
    SIMPLE = "simple"
    DETAILED = "detailed"
    MINIMAL = "minimal"
    COMPACT = "compact"
```

**使用例:**
```python
from minto.logging_config import LogFormat
config = LogConfig(format=LogFormat.DETAILED)
```

### LogConfig

ログ設定を管理するデータクラスです。

```python
@dataclass
class LogConfig:
    enabled: bool = True
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.DETAILED
    show_timestamps: bool = True
    show_icons: bool = True
    show_colors: bool = True
    show_details: bool = True
    max_value_length: Optional[int] = 200
```

**パラメータ:**
- `enabled`: ログ機能の有効/無効
- `level`: 出力するログレベル
- `format`: ログの表示フォーマット
- `show_timestamps`: タイムスタンプの表示
- `show_icons`: アイコンの表示
- `show_colors`: カラー表示
- `show_details`: 詳細情報の表示
- `max_value_length`: 値の最大表示長（Noneで制限なし）

**メソッド:**

#### should_log(level: LogLevel) -> bool
指定されたレベルのログを出力すべきかを判定します。

```python
config = LogConfig(level=LogLevel.WARNING)
print(config.should_log(LogLevel.INFO))    # False
print(config.should_log(LogLevel.ERROR))   # True
```

### LogFormatter

ログメッセージのフォーマットを行うクラスです。

```python
class LogFormatter:
    def __init__(self, config: LogConfig):
        self.config = config
        self._indent_level = 0
```

**メソッド:**

#### format_message(level: LogLevel, message: str, **kwargs) -> str
ログメッセージをフォーマットします。

**パラメータ:**
- `level`: ログレベル
- `message`: メッセージ内容
- `**kwargs`: 追加のフォーマット情報

#### set_indent_level(level: int)
インデントレベルを設定します。

#### increment_indent()
インデントレベルを1つ増やします。

#### decrement_indent()
インデントレベルを1つ減らします。

#### truncate_value(value: Any, max_length: Optional[int] = None) -> str
値を指定された長さで切り詰めます。

## minto.logger

### MintoLogger

メインのログ機能を提供するクラスです。

```python
class MintoLogger:
    def __init__(self, config: Optional[LogConfig] = None):
        self.config = config or LogConfig()
        self.formatter = LogFormatter(self.config)
```

**実験ライフサイクルメソッド:**

#### log_experiment_start(name: str)
実験開始をログします。

```python
logger.log_experiment_start("my_experiment")
```

#### log_experiment_end(name: str, duration: float, num_runs: int)
実験終了をログします。

**パラメータ:**
- `name`: 実験名
- `duration`: 実行時間（秒）
- `num_runs`: 実行されたラン数

#### log_environment_info(env_info: Dict[str, Any])
環境情報をログします。

**ランライフサイクルメソッド:**

#### log_run_start(run_id: int)
ラン開始をログします。

#### log_run_end(run_id: int, duration: float)
ラン終了をログします。

**データログメソッド:**

#### log_parameter(key: str, value: Any)
パラメータをログします。

```python
logger.log_parameter("temperature", 1.0)
logger.log_parameter("solver_type", "OpenJij")
```

#### log_object(key: str, obj: Any, description: Optional[str] = None)
オブジェクトをログします。

```python
logger.log_object("problem_data", data_dict, "QUBO problem instance")
```

#### log_solution(key: str, solution: Any)
解をログします。

```python
logger.log_solution("best_solution", [1, 0, 1, 0, 1])
```

#### log_sampleset(key: str, num_samples: int, best_energy: Optional[float] = None)
サンプルセットをログします。

```python
logger.log_sampleset("results", 1000, -42.5)
```

#### log_solver(name: str, execution_time: Optional[float] = None)
ソルバー実行をログします。

**診断メソッド:**

#### log_debug(message: str)
DEBUGレベルのメッセージをログします。

#### log_info(message: str)
INFOレベルのメッセージをログします。

#### log_warning(message: str)
WARNINGレベルのメッセージをログします。

#### log_error(message: str)
ERRORレベルのメッセージをログします。

#### log_critical(message: str)
CRITICALレベルのメッセージをログします。

### グローバル関数

#### configure_logging(**kwargs)
グローバルログ設定を行います。

```python
from minto.logger import configure_logging
from minto.logging_config import LogLevel

configure_logging(
    enabled=True,
    level=LogLevel.DEBUG,
    show_timestamps=True,
    show_colors=False
)
```

**パラメータ:** `LogConfig` クラスと同じパラメータを受け取ります。

#### get_logger() -> MintoLogger
グローバル設定されたロガーインスタンスを取得します。

```python
from minto.logger import get_logger

logger = get_logger()
logger.log_experiment_start("global_experiment")
```

## Experimentクラスの拡張

### 新しいパラメータ

#### verbose_logging: bool = False
ログ機能の有効/無効を制御します。

#### log_config: Optional[LogConfig] = None
カスタムログ設定を指定します。未指定時はグローバル設定を使用します。

### 新しいメソッド

#### finish_experiment()
実験を終了し、統計情報をログします。

```python
exp = Experiment(name="test", verbose_logging=True)
# ... 実験実行 ...
exp.finish_experiment()
```

## Runクラスの拡張

### 新しいメソッド

#### log_solver(name: str, solver_func: Callable, exclude_params: Optional[List[str]] = None) -> Callable
ソルバー関数をラップしてパラメータと実行時間を自動でログします。

```python
def my_solver(param1, param2, secret_key):
    return {"result": "success"}

with run:
    wrapped_solver = run.log_solver(
        "my_solver", 
        my_solver,
        exclude_params=["secret_key"]
    )
    result = wrapped_solver(param1=10, param2="test", secret_key="hidden")
```

**パラメータ:**
- `name`: ソルバー名
- `solver_func`: ラップするソルバー関数
- `exclude_params`: ログから除外するパラメータ名のリスト

**戻り値:** ラップされたソルバー関数

## 使用例

### 基本的な使用法

```python
from minto import Experiment

exp = Experiment(name="api_example", verbose_logging=True)
run = exp.create_run()

with run:
    run.log_parameter("method", "QAOA")
    run.log_parameter("layers", 3)
    run.log_solution("result", [1, 0, 1])

exp.finish_experiment()
```

### カスタム設定

```python
from minto import Experiment
from minto.logging_config import LogConfig, LogLevel, LogFormat

config = LogConfig(
    level=LogLevel.DEBUG,
    format=LogFormat.SIMPLE,
    show_timestamps=False
)

exp = Experiment(
    name="custom_example",
    verbose_logging=True,
    log_config=config
)
```

### グローバル設定

```python
from minto.logger import configure_logging, get_logger
from minto.logging_config import LogLevel

configure_logging(level=LogLevel.WARNING, show_colors=False)

logger = get_logger()
logger.log_experiment_start("global_example")
```

## エラーハンドリング

ログ機能は設計上、エラーが発生してもメイン処理を中断しないよう実装されています。ログ出力でエラーが発生した場合は、内部的に処理され、実験の実行には影響しません。

## パフォーマンス

- `verbose_logging=False` 時: オーバーヘッドなし
- `verbose_logging=True` 時: 実験処理時間に対して1%未満の影響
- メモリ使用量: 追加のメモリ使用は軽微

ログ機能は効率的に設計されており、本番環境での使用にも適しています。
