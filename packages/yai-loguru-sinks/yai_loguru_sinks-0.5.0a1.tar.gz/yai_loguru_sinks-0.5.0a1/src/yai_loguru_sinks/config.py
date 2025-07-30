"""loguru-config 扩展配置

注册企业级 sink 协议解析器，目前专注于阿里云 SLS 支持。
"""

import re
from typing import Any, Dict, Callable
from .sls import parse_sls_url, create_sls_sink

# 检查 loguru-config 是否可用
try:
    from loguru_config import LoguruConfig
    HAS_LOGURU_CONFIG = True
except ImportError:
    HAS_LOGURU_CONFIG = False


def sls_protocol_parser(url: str) -> Any:
    """SLS 协议解析器
    
    解析 sls:// URL 并创建对应的 sink 函数
    
    Args:
        url: SLS URL，格式如 sls://project/logstore?region=cn-hangzhou&topic=app
        
    Returns:
        配置好的 SLS sink 函数
    """
    config = parse_sls_url(url)
    return create_sls_sink(**config)


def cloudwatch_protocol_parser(sink_config: str) -> Callable:
    """CloudWatch 协议解析器（占位符）
    
    Args:
        sink_config: CloudWatch URL 配置
    
    Returns:
        CloudWatch sink 函数（暂未实现）
    """
    raise NotImplementedError("CloudWatch sink 暂未实现")


def elasticsearch_protocol_parser(sink_config: str) -> Callable:
    """Elasticsearch 协议解析器（占位符）
    
    Args:
        sink_config: Elasticsearch URL 配置
    
    Returns:
        Elasticsearch sink 函数（暂未实现）
    """
    raise NotImplementedError("Elasticsearch sink 暂未实现")


def kafka_protocol_parser(sink_config: str) -> Callable:
    """Kafka 协议解析器（占位符）
    
    Args:
        sink_config: Kafka URL 配置
    
    Returns:
        Kafka sink 函数（暂未实现）
    """
    raise NotImplementedError("Kafka sink 暂未实现")


# 协议解析器映射 - 使用元组格式 (regex, parser_function)
PROTOCOL_PARSERS = [
    (re.compile(r'^sls://(.*)$'), lambda self, url: sls_protocol_parser(f"sls://{url}")),
    (re.compile(r'^cloudwatch://(.*)$'), lambda self, url: cloudwatch_protocol_parser(f"cloudwatch://{url}")),
    (re.compile(r'^elasticsearch://(.*)$'), lambda self, url: elasticsearch_protocol_parser(f"elasticsearch://{url}")),
    (re.compile(r'^kafka://(.*)$'), lambda self, url: kafka_protocol_parser(f"kafka://{url}")),
]


def setup_extended_config() -> None:
    """设置扩展的 loguru-config 协议解析器
    
    注册企业级 sink 协议解析器到 loguru-config。
    调用此函数后，可以在配置文件中使用 sls://、cloudwatch:// 等协议。
    
    Raises:
        ImportError: 如果 loguru-config 未安装
    """
    if not HAS_LOGURU_CONFIG:
        raise ImportError(
            "loguru-config 未安装，请运行: uv add loguru-config"
        )
    
    # 注册协议解析器 - 使用列表扩展方式
    if hasattr(LoguruConfig, 'supported_protocol_parsers'):
        # 将现有的解析器转换为列表并添加新的解析器
        current_parsers = list(LoguruConfig.supported_protocol_parsers)
        LoguruConfig.supported_protocol_parsers = current_parsers + PROTOCOL_PARSERS
    else:
        # 如果 loguru-config 版本不支持协议解析器，提供警告
        import warnings
        warnings.warn(
            "当前 loguru-config 版本不支持协议解析器，请升级到最新版本",
            UserWarning
        )


def create_config_from_dict(config_dict: Dict[str, Any]) -> LoguruConfig:
    """从字典创建 LoguruConfig
    
    Args:
        config_dict: 配置字典
        
    Returns:
        配置好的 LoguruConfig 实例
    """
    config = LoguruConfig()
    config.load(config_dict)
    return config


def create_config_from_file(config_file: str) -> LoguruConfig:
    """从文件创建 LoguruConfig
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置好的 LoguruConfig 实例
    """
    config = LoguruConfig()
    config.load(config_file)
    return config