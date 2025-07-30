"""
阿里云 SLS (Simple Log Service) Sink 工厂

提供创建 SLS sink 的工厂函数，支持批量发送和异步处理。
"""

import os
import json
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from queue import Queue, Empty
from urllib.parse import urlparse, parse_qs

try:
    from aliyun.log import LogClient  # type: ignore
    from aliyun.log.logitem import LogItem  # type: ignore
    from aliyun.log.putlogsrequest import PutLogsRequest  # type: ignore
    HAS_ALIYUN_SDK = True
except ImportError:
    HAS_ALIYUN_SDK = False
    LogClient = None
    LogItem = None
    PutLogsRequest = None


@dataclass
class SlsConfig:
    """SLS Sink 配置"""
    
    # SLS 连接配置
    endpoint: str
    access_key_id: str
    access_key_secret: str
    project: str
    logstore: str
    
    # SLS 特定配置
    topic: str = "python-app"
    source: str = "yai-loguru"
    
    # 批量发送配置
    batch_size: int = 100
    flush_interval: float = 5.0
    max_retries: int = 3
    timeout: float = 30.0
    
    # 其他配置
    compress: bool = True


class SlsSink:
    """SLS Sink 实现类"""
    
    def __init__(self, config: SlsConfig):
        if not HAS_ALIYUN_SDK:
            raise ImportError(
                "阿里云 SDK 未安装，请运行: uv add aliyun-log-python-sdk"
            )
        
        self.config = config
        self.client = LogClient(
            config.endpoint,
            config.access_key_id,
            config.access_key_secret
        )
        
        # 初始化队列和线程
        self.log_queue: Queue = Queue()
        self.stop_event = threading.Event()
        self.flush_thread = threading.Thread(target=self._flush_worker, daemon=True)
        self.flush_thread.start()
    
    def __call__(self, message):
        """Loguru sink 调用接口"""
        try:
            record = message.record
            
            # 构造日志数据
            log_data = {
                'timestamp': record['time'].timestamp(),
                'level': record['level'].name,
                'message': str(record['message']),
                'module': record.get('name', ''),
                'function': record.get('function', ''),
                'line': record.get('line', 0),
            }
            
            self.log_queue.put(log_data)
                
        except Exception as e:
            # 避免日志处理错误影响主程序
            print(f"SLS日志处理错误: {e}")
    
    def _flush_worker(self):
        """后台线程工作函数，定期刷新日志"""
        messages = []
        
        while not self.stop_event.is_set():
            try:
                # 收集消息
                try:
                    # 等待消息或超时
                    message = self.log_queue.get(timeout=self.config.flush_interval)
                    messages.append(message)
                    
                    # 继续收集直到批量大小或队列为空
                    while len(messages) < self.config.batch_size:
                        try:
                            message = self.log_queue.get_nowait()
                            messages.append(message)
                        except Empty:
                            break
                            
                except Empty:
                    # 超时，如果有消息就发送
                    pass
                
                # 发送消息
                if messages:
                    self._send_messages(messages)
                    messages.clear()
                    
            except Exception as e:
                print(f"SLS刷新工作线程错误: {e}")
                time.sleep(1)  # 避免错误循环
    
    def _send_messages(self, messages: List[Dict[str, Any]]):
        """发送消息到SLS"""
        if not messages:
            return
        
        try:
            # 转换为SLS LogItem格式
            log_items = []
            for msg in messages:
                log_item = LogItem()
                log_item.set_time(int(msg['timestamp']))
                log_item.set_contents([
                    ('level', msg['level']),
                    ('message', msg['message']),
                    ('module', msg['module']),
                    ('function', msg['function']),
                    ('line', str(msg['line'])),
                ])
                log_items.append(log_item)
            
            # 创建请求
            request = PutLogsRequest(
                project=self.config.project,
                logstore=self.config.logstore,
                topic=self.config.topic,
                source=self.config.source,
                logitems=log_items,
                compress=self.config.compress
            )
            
            # 发送到SLS
            response = self.client.put_logs(request)
            
            if not response.is_success():
                print(f"SLS发送失败: {response.get_error_message()}")
                
        except Exception as e:
            print(f"SLS消息发送错误: {e}")
    
    def close(self):
        """关闭 sink，发送剩余日志"""
        self.stop_event.set()
        
        if self.flush_thread.is_alive():
            self.flush_thread.join(timeout=5.0)
        
        # 发送剩余的日志
        messages = []
        try:
            while not self.log_queue.empty():
                messages.append(self.log_queue.get_nowait())
        except Empty:
            pass
        
        if messages:
            self._send_messages(messages)


def create_sls_sink(
    project: str,
    logstore: str,
    region: str,
    access_key_id: Optional[str] = None,
    access_key_secret: Optional[str] = None,
    topic: str = "python-app",
    source: str = "yai-loguru",
    batch_size: int = 100,
    flush_interval: float = 5.0,
    compress: bool = True,
    **kwargs
) -> Callable:
    """创建 SLS sink 函数
    
    Args:
        project: SLS 项目名
        logstore: SLS 日志库名
        region: 阿里云区域，如 'cn-hangzhou'
        access_key_id: 访问密钥ID，默认从环境变量 SLS_ACCESS_KEY_ID 获取
        access_key_secret: 访问密钥，默认从环境变量 SLS_ACCESS_KEY_SECRET 获取
        topic: 日志主题
        source: 日志来源
        batch_size: 批量发送大小
        flush_interval: 刷新间隔（秒）
        compress: 是否压缩
        **kwargs: 其他配置参数
    
    Returns:
        可调用的 sink 函数
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
    
    # 构造 endpoint
    endpoint = f"https://{region}.log.aliyuncs.com"
    
    config = SlsConfig(
        endpoint=endpoint,
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        project=project,
        logstore=logstore,
        topic=topic,
        source=source,
        batch_size=batch_size,
        flush_interval=flush_interval,
        compress=compress,
    )
    
    return SlsSink(config)


def parse_sls_url(url: str) -> Dict[str, Any]:
    """解析 SLS URL 格式: sls://project/logstore?region=xxx&access_key_id=xxx&access_key_secret=xxx
    
    Args:
        url: SLS URL
        
    Returns:
        解析后的配置字典
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