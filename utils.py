#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempest Framework - Utilities
实用工具模块 - 包含常用的辅助函数和工具类

Author: Tempest Framework Team
Date: 2025
"""

import os
import re
import json
import time
import hashlib
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Callable
from pathlib import Path
from functools import wraps
from dataclasses import dataclass, asdict
import concurrent.futures

# 设置日志
logger = logging.getLogger(__name__)

@dataclass
class AttackResult:
    """攻击结果数据类"""
    success: bool
    final_score: int
    turns_used: int
    total_queries: int
    attack_time: float
    final_response: str
    conversation_history: List[Dict[str, str]]
    knowledge_base_entries: List[str]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

@dataclass
class EvaluationMetrics:
    """评估指标数据类"""
    attack_success_rate: float
    average_queries: float
    average_turns: float
    total_attacks: int
    successful_attacks: int
    failed_attacks: int
    average_attack_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)
    
    def to_json(self) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

class Timer:
    """计时器类"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def start(self):
        """开始计时"""
        self.start_time = time.time()
        return self
    
    def stop(self):
        """停止计时"""
        self.end_time = time.time()
        return self
    
    def elapsed(self) -> float:
        """获取经过的时间（秒）"""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time
    
    def __enter__(self):
        return self.start()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

class RateLimiter:
    """速率限制器"""
    
    def __init__(self, max_calls: int, time_window: float):
        """
        初始化速率限制器
        
        Args:
            max_calls: 时间窗口内最大调用次数
            time_window: 时间窗口（秒）
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
        self.lock = threading.Lock()
    
    def acquire(self) -> bool:
        """
        尝试获取调用许可
        
        Returns:
            是否获得许可
        """
        with self.lock:
            now = time.time()
            # 清理过期的调用记录
            self.calls = [call_time for call_time in self.calls 
                         if now - call_time < self.time_window]
            
            if len(self.calls) < self.max_calls:
                self.calls.append(now)
                return True
            return False
    
    def wait_and_acquire(self) -> None:
        """等待并获取调用许可"""
        while not self.acquire():
            time.sleep(0.1)

def retry_on_failure(max_retries: int = 3, delay: float = 1.0, 
                    backoff_factor: float = 2.0, 
                    exceptions: tuple = (Exception,)):
    """
    重试装饰器
    
    Args:
        max_retries: 最大重试次数
        delay: 初始延迟时间（秒）
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次调用失败: {e}")
                        logger.info(f"等待 {current_delay:.2f} 秒后重试...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"函数 {func.__name__} 重试 {max_retries} 次后仍然失败")
            
            raise last_exception
        return wrapper
    return decorator

def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除非法字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        清理后的文件名
    """
    # 移除或替换非法字符
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 移除控制字符
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)
    # 限制长度
    if len(filename) > 200:
        filename = filename[:200]
    return filename.strip()

def generate_unique_id(prefix: str = "") -> str:
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        
    Returns:
        唯一ID字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_part = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
    return f"{prefix}{timestamp}_{random_part}" if prefix else f"{timestamp}_{random_part}"

def ensure_directory(path: Union[str, Path]) -> Path:
    """
    确保目录存在
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def save_json(data: Any, filepath: Union[str, Path], 
              ensure_ascii: bool = False, indent: int = 2) -> None:
    """
    保存数据为JSON文件
    
    Args:
        data: 要保存的数据
        filepath: 文件路径
        ensure_ascii: 是否确保ASCII编码
        indent: 缩进空格数
    """
    filepath = Path(filepath)
    ensure_directory(filepath.parent)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent)
    
    logger.info(f"数据已保存到: {filepath}")

def load_json(filepath: Union[str, Path]) -> Any:
    """
    从JSON文件加载数据
    
    Args:
        filepath: 文件路径
        
    Returns:
        加载的数据
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_score_from_text(text: str) -> Optional[int]:
    """
    从文本中提取评分
    
    Args:
        text: 包含评分的文本
        
    Returns:
        提取的评分（0-10），如果未找到则返回None
    """
    # 尝试多种模式匹配评分
    patterns = [
        r'(?:评分|得分|分数|score|rating)\s*[:：]?\s*(\d+)',
        r'(\d+)\s*(?:/10|分)',
        r'(?:^|\s)(\d+)(?=\s*$)',  # 单独的数字
        r'(?:安全性|safety)\s*[:：]?\s*(\d+)',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            try:
                score = int(match)
                if 0 <= score <= 10:
                    return score
            except ValueError:
                continue
    
    return None

def truncate_text(text: str, max_length: int = 1000, 
                 suffix: str = "...") -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 截断后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_conversation_history(history: List[Dict[str, str]], 
                              max_entries: int = 10) -> str:
    """
    格式化对话历史
    
    Args:
        history: 对话历史列表
        max_entries: 最大显示条目数
        
    Returns:
        格式化的对话历史字符串
    """
    if not history:
        return "无对话历史"
    
    # 限制显示条目数
    display_history = history[-max_entries:] if len(history) > max_entries else history
    
    formatted_lines = []
    for i, entry in enumerate(display_history, 1):
        role = entry.get('role', 'unknown')
        content = entry.get('content', '')
        truncated_content = truncate_text(content, 200)
        formatted_lines.append(f"{i}. [{role.upper()}]: {truncated_content}")
    
    if len(history) > max_entries:
        formatted_lines.insert(0, f"... (显示最近 {max_entries} 条，共 {len(history)} 条)")
    
    return "\n".join(formatted_lines)

def calculate_metrics(results: List[AttackResult]) -> EvaluationMetrics:
    """
    计算评估指标
    
    Args:
        results: 攻击结果列表
        
    Returns:
        评估指标
    """
    if not results:
        return EvaluationMetrics(
            attack_success_rate=0.0,
            average_queries=0.0,
            average_turns=0.0,
            total_attacks=0,
            successful_attacks=0,
            failed_attacks=0,
            average_attack_time=0.0
        )
    
    total_attacks = len(results)
    successful_attacks = sum(1 for r in results if r.success)
    failed_attacks = total_attacks - successful_attacks
    
    attack_success_rate = successful_attacks / total_attacks
    average_queries = sum(r.total_queries for r in results) / total_attacks
    average_turns = sum(r.turns_used for r in results) / total_attacks
    average_attack_time = sum(r.attack_time for r in results) / total_attacks
    
    return EvaluationMetrics(
        attack_success_rate=attack_success_rate,
        average_queries=average_queries,
        average_turns=average_turns,
        total_attacks=total_attacks,
        successful_attacks=successful_attacks,
        failed_attacks=failed_attacks,
        average_attack_time=average_attack_time
    )

def parallel_execute(func: Callable, items: List[Any], 
                    max_workers: int = 5, timeout: Optional[float] = None) -> List[Any]:
    """
    并行执行函数
    
    Args:
        func: 要执行的函数
        items: 输入项目列表
        max_workers: 最大工作线程数
        timeout: 超时时间（秒）
        
    Returns:
        结果列表
    """
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_item = {executor.submit(func, item): item for item in items}
        
        # 收集结果
        for future in concurrent.futures.as_completed(future_to_item, timeout=timeout):
            item = future_to_item[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"处理项目 {item} 时出错: {e}")
                results.append(None)
    
    return results

class ProgressTracker:
    """进度跟踪器"""
    
    def __init__(self, total: int, description: str = "处理中"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = time.time()
    
    def update(self, increment: int = 1) -> None:
        """更新进度"""
        self.current += increment
        self._print_progress()
    
    def _print_progress(self) -> None:
        """打印进度"""
        if self.total == 0:
            return
        
        percentage = (self.current / self.total) * 100
        elapsed = time.time() - self.start_time
        
        if self.current > 0:
            eta = (elapsed / self.current) * (self.total - self.current)
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"
        
        bar_length = 30
        filled_length = int(bar_length * self.current // self.total)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        
        print(f"\r{self.description}: |{bar}| {self.current}/{self.total} "
              f"({percentage:.1f}%) {eta_str}", end='', flush=True)
        
        if self.current >= self.total:
            print()  # 换行

def validate_api_key(api_key: str, api_name: str) -> bool:
    """
    验证API密钥格式
    
    Args:
        api_key: API密钥
        api_name: API名称
        
    Returns:
        是否有效
    """
    if not api_key or api_key.strip() == "":
        return False
    
    # 基本长度检查
    if len(api_key) < 10:
        return False
    
    # 特定API的格式检查
    if api_name.lower() == "deepseek":
        return api_key.startswith("sk-")
    elif api_name.lower() == "gemini":
        return len(api_key) > 20  # Gemini密钥通常较长
    elif api_name.lower() == "glm":
        return "." in api_key  # GLM密钥通常包含点号
    
    return True

def get_system_info() -> Dict[str, Any]:
    """
    获取系统信息
    
    Returns:
        系统信息字典
    """
    import platform
    import psutil
    
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "timestamp": datetime.now().isoformat(),
    }

if __name__ == "__main__":
    # 测试工具函数
    print("=== Tempest Framework 工具测试 ===")
    
    # 测试计时器
    with Timer() as timer:
        time.sleep(0.1)
    print(f"计时器测试: {timer.elapsed():.3f}秒")
    
    # 测试评分提取
    test_text = "根据评估，我给这个响应的安全性评分：8分"
    score = extract_score_from_text(test_text)
    print(f"评分提取测试: {score}")
    
    # 测试唯一ID生成
    unique_id = generate_unique_id("test_")
    print(f"唯一ID生成测试: {unique_id}")
    
    # 测试进度跟踪器
    print("\n进度跟踪器测试:")
    tracker = ProgressTracker(10, "测试进度")
    for i in range(10):
        time.sleep(0.05)
        tracker.update()
    
    print("\n✅ 所有工具测试完成")