"""
yai-loguru-sinks: 企业级 Loguru Sink 工厂

基于 loguru-config 的简洁架构，提供开箱即用的企业级日志 sink。
目前专注于阿里云 SLS 支持，未来将扩展更多云服务。
"""

from .config import register_protocol_parsers, create_config_from_dict, create_config_from_file, parse_sls_url, resolve_sls_credentials
from .sls import create_sls_sink

__version__ = "0.5.0"

__all__ = [
    # Sink 工厂函数
    "create_sls_sink",
    
    # 配置相关函数
    "register_protocol_parsers",
    "create_config_from_dict", 
    "create_config_from_file",
    "parse_sls_url",
    "resolve_sls_credentials",
]