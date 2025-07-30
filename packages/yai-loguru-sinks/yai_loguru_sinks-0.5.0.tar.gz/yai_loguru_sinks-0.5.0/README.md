# yai-loguru-sinks

企业级 Loguru Sink 工厂库，基于 `loguru-config` 提供统一的配置驱动体验。

## 核心理念

- **简洁架构**：移除复杂的插件抽象，直接提供 sink 工厂函数
- **配置驱动**：基于 `loguru-config` 的统一配置体验
- **企业级**：专注于阿里云 SLS 日志服务
- **原生兼容**：完全兼容 Loguru 的 sink 机制

## 快速开始

### 安装

```bash
uv add yai-loguru-sinks
```

### 基本使用

```python
from yai_loguru_sinks import setup_extended_config
from loguru_config import LoguruConfig

# 注册企业级协议解析器
setup_extended_config()

# 配置驱动，一行搞定
config = LoguruConfig()
config.load('logging.yaml')
```

### 配置文件示例

```yaml
# logging.yaml
handlers:
  # 阿里云 SLS
  - sink: sls://my-project/my-logstore?region=cn-hangzhou&access_key_id=${SLS_ACCESS_KEY}&access_key_secret=${SLS_SECRET}
    level: WARNING
    format: '{time} | {level} | {message}'
    
  # 本地文件（Loguru 原生）
  - sink: logs/app.log
    rotation: "1 day"
    retention: "30 days"
    compression: "gz"
```

## 支持的 Sink 类型

### 阿里云 SLS
```yaml
sink: sls://project/logstore?region=cn-hangzhou&access_key_id=xxx&access_key_secret=xxx
```

## 直接使用 Sink 工厂

如果不使用配置文件，也可以直接调用 sink 工厂：

```python
from loguru import logger
from yai_loguru_sinks.sls import create_sls_sink

# 创建 SLS sink
sls_sink = create_sls_sink(
    project="my-project",
    logstore="my-logstore",
    region="cn-hangzhou",
    access_key_id="xxx",
    access_key_secret="xxx"
)

# 添加到 logger
logger.add(sls_sink, level="WARNING")
```

## 架构优势

### 相比传统插件系统
- ✅ **移除冗余抽象**：不再需要 `LoguruPlugin` 基类
- ✅ **简化使用方式**：统一的配置文件格式
- ✅ **利用成熟生态**：基于 `loguru-config` 的稳定基础
- ✅ **保持功能完整**：所有企业级功能都保留

### 设计原则
1. **职责分离**：`loguru` 负责基础功能，`yai-loguru-sinks` 负责企业级扩展
2. **配置驱动**：通过 YAML/JSON 配置，而非代码硬编码
3. **协议扩展**：利用 `loguru-config` 的协议解析机制
4. **工厂模式**：提供灵活的 sink 创建函数

## 许可证

MIT License