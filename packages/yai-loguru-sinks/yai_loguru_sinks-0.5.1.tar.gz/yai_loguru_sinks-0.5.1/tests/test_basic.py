"""yai-loguru-sinks 基础测试

测试新的 sink 工厂模式的核心功能。
专注于阿里云 SLS 支持。"""

import pytest
import os
from unittest.mock import patch, MagicMock


class TestSlsSink:
    """测试 SLS Sink 功能"""
    
    def test_create_sls_sink(self):
        """测试创建 SLS sink"""
        from yai_loguru_sinks import create_sls_sink
        
        sink = create_sls_sink(
            project="test-project",
            logstore="test-logstore",
            region="cn-hangzhou",
            access_key_id="test-key",
            access_key_secret="test-secret"
        )
        
        assert callable(sink)
    
    def test_parse_sls_url(self):
        """测试 SLS URL 解析"""
        from yai_loguru_sinks.config import parse_sls_url
        
        # 基本 URL
        config = parse_sls_url("sls://project/logstore?region=cn-hangzhou")
        assert config["project"] == "project"
        assert config["logstore"] == "logstore"
        assert config["region"] == "cn-hangzhou"
        
        # 带参数的 URL
        config = parse_sls_url(
            "sls://project/logstore?region=cn-beijing&topic=app&batch_size=100"
        )
        assert config["region"] == "cn-beijing"
        assert config["topic"] == "app"
        assert config["batch_size"] == 100


class TestConfigIntegration:
    """测试配置集成功能"""
    
    def test_register_protocol_parsers(self):
        """测试注册协议解析器"""
        from yai_loguru_sinks import register_protocol_parsers
        
        # 应该不抛出异常
        register_protocol_parsers()
    
    @patch.dict(os.environ, {
        'SLS_ACCESS_KEY_ID': 'test-key',
        'SLS_ACCESS_KEY_SECRET': 'test-secret'
    })
    def test_sls_protocol_parser(self):
        """测试 SLS 协议解析器"""
        from yai_loguru_sinks.config import sls_protocol_parser
        
        # 测试基本解析
        sink = sls_protocol_parser("sls://project/logstore?region=cn-hangzhou")
        assert callable(sink)
    
    @patch.dict(os.environ, {
        'SLS_ACCESS_KEY_ID': 'test-key',
        'SLS_ACCESS_KEY_SECRET': 'test-secret'
    })
    def test_sls_protocol_parser_with_env(self):
        """测试带环境变量的 SLS 协议解析器"""
        from yai_loguru_sinks.config import sls_protocol_parser
        
        sink = sls_protocol_parser("sls://project/logstore?region=cn-hangzhou")
        assert callable(sink)


class TestPackageImports:
    """测试包导入功能"""
    
    def test_main_imports(self):
        """测试主要导入"""
        from yai_loguru_sinks import register_protocol_parsers, create_sls_sink
        
        assert callable(register_protocol_parsers)
        assert callable(create_sls_sink)
    
    def test_version_import(self):
        """测试版本导入"""
        from yai_loguru_sinks import __version__
        
        assert isinstance(__version__, str)
        assert len(__version__) > 0


class TestErrorHandling:
    """测试错误处理"""
    
    def test_invalid_sls_url(self):
        """测试无效的 SLS URL"""
        from yai_loguru_sinks.config import parse_sls_url
        
        with pytest.raises(ValueError):
            parse_sls_url("invalid://url")
        
        with pytest.raises(ValueError):
            parse_sls_url("sls://project/logstore")  # 缺少 region 参数
        
        with pytest.raises(ValueError):
            parse_sls_url("sls://project?region=cn-hangzhou")  # 缺少 logstore
    
    def test_missing_credentials(self):
        """测试缺失凭证"""
        from yai_loguru_sinks import create_sls_sink
        
        # 不提供凭证应该抛出异常
        with pytest.raises((ValueError, TypeError)):
            create_sls_sink(
                project="test",
                logstore="test",
                region="cn-hangzhou"
                # 缺少 access_key_id 和 access_key_secret
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])