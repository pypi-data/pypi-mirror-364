"""loguru-config 扩展配置

注册企业级 sink 协议解析器，目前专注于阿里云 SLS 支持。
"""

import os
import re
from typing import Any, Dict, Callable, Optional
from urllib.parse import urlparse, parse_qs

# 检查 loguru-config 是否可用
try:
    from loguru_config import LoguruConfig
    HAS_LOGURU_CONFIG = True
except ImportError:
    HAS_LOGURU_CONFIG = False


def resolve_sls_credentials(
    access_key_id: Optional[str] = None,
    access_key_secret: Optional[str] = None
) -> tuple[str, str]:
    """解析 SLS 认证信息
    
    优先使用传入的参数，如果为空则从环境变量获取
    
    Args:
        access_key_id: 访问密钥ID，可选
        access_key_secret: 访问密钥，可选
        
    Returns:
        (access_key_id, access_key_secret) 元组
        
    Raises:
        ValueError: 如果无法获取完整的认证信息
    """
    # 从环境变量获取认证信息
    if not access_key_id:
        access_key_id = os.getenv("SLS_ACCESS_KEY_ID")
    if not access_key_secret:
        access_key_secret = os.getenv("SLS_ACCESS_KEY_SECRET")
    
    if not access_key_id or not access_key_secret:
        raise ValueError(
            "SLS 认证信息缺失，请提供 access_key_id 和 access_key_secret "
            "或设置环境变量 SLS_ACCESS_KEY_ID 和 SLS_ACCESS_KEY_SECRET"
        )
    
    return access_key_id, access_key_secret


def parse_sls_url(url: str) -> Dict[str, Any]:
    """解析 SLS URL 格式
    
    支持的 URL 格式：
        sls://project/logstore?region=xxx&access_key_id=xxx&access_key_secret=xxx
    
    完整示例：
        sls://yai-log-test/app-log?region=cn-beijing&topic=python-app&batch_size=100&flush_interval=5.0&compress=true
        sls://my-project/error-log?region=cn-hangzhou&access_key_id=LTAI5xxx&access_key_secret=xxx&source=web-server
    
    必需参数：
        - project: 阿里云 SLS 项目名
        - logstore: 日志库名
        - region: 地域，如 cn-beijing, cn-hangzhou, cn-shanghai
    
    可选参数：
        - access_key_id: 访问密钥 ID（可通过环境变量 SLS_ACCESS_KEY_ID 设置）
        - access_key_secret: 访问密钥（可通过环境变量 SLS_ACCESS_KEY_SECRET 设置）
        - topic: 日志主题，默认 "python-app"
        - source: 日志来源，默认 "yai-loguru"
        - batch_size: 批量发送大小，默认 100
        - flush_interval: 刷新间隔（秒），默认 5.0
        - compress: 是否压缩，默认 true
    
    Args:
        url: SLS URL 字符串
        
    Returns:
        解析后的配置字典
        
    Raises:
        ValueError: URL 格式无效或缺少必需参数
    """
    parsed = urlparse(url)
    
    if parsed.scheme != 'sls':
        raise ValueError(f"无效的 SLS URL scheme: {parsed.scheme}")
    
    # 解析路径，project 在 netloc 中，logstore 在 path 中
    project = parsed.netloc
    logstore = parsed.path.strip('/')
    
    if not project:
        raise ValueError(f"无效的 SLS URL: 缺少项目名")
    
    if not logstore:
        raise ValueError(f"无效的 SLS URL: 缺少日志库名")
    
    # 解析查询参数
    query_params = parse_qs(parsed.query)
    
    # 提取必需参数
    region = query_params.get('region', [None])[0]
    if not region:
        raise ValueError("SLS URL 缺少 region 参数")
    
    config: Dict[str, Any] = {
        'project': project,
        'logstore': logstore,
        'region': region,
    }
    
    # 提取可选参数
    optional_params = [
        'access_key_id', 'access_key_secret', 'topic', 'source',
        'batch_size', 'flush_interval', 'compress'
    ]
    
    for param in optional_params:
        if param in query_params:
            raw_value = query_params[param][0]
            # 类型转换
            if param in ['batch_size']:
                config[param] = int(raw_value)
            elif param in ['flush_interval']:
                config[param] = float(raw_value)
            elif param in ['compress']:
                config[param] = raw_value.lower() in ('true', '1', 'yes')
            else:
                config[param] = raw_value
    
    return config


def sls_protocol_parser(url: str) -> Any:
    """SLS 协议解析器
    
    解析 sls:// URL 并创建对应的 sink 函数
    
    Args:
        url: SLS URL，格式如 sls://project/logstore?region=cn-hangzhou&topic=app
        
    Returns:
        配置好的 SLS sink 函数
    """
    from .sls import create_sls_sink  # 延迟导入避免循环依赖
    config = parse_sls_url(url)
    
    # 解析认证信息
    access_key_id, access_key_secret = resolve_sls_credentials(
        config.get('access_key_id'),
        config.get('access_key_secret')
    )
    config['access_key_id'] = access_key_id
    config['access_key_secret'] = access_key_secret
    
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


def register_protocol_parsers() -> None:
    """注册协议解析器到 loguru-config
    
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