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
            
            # 注意：put_logs 如果成功不会抛出异常，失败会抛出 LogException
            # 所以这里不需要检查 is_success()，能执行到这里说明发送成功
                
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
    from .config import resolve_sls_credentials
    
    # 解析认证信息（统一在 config.py 中处理）
    access_key_id, access_key_secret = resolve_sls_credentials(
        access_key_id, access_key_secret
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