#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tempest Framework - Configuration Loader
配置加载器 - 用于读取和管理YAML配置文件

Author: Tempest Framework Team
Date: 2025
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional
from pathlib import Path

class ConfigLoader:
    """配置加载器类"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = {}
        self.logger = logging.getLogger(__name__)
        
        # 加载配置
        self.load_config()
        
    def load_config(self) -> None:
        """加载配置文件"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
                self.logger.info(f"配置文件加载成功: {self.config_path}")
            else:
                self.logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
                self.config = self._get_default_config()
                
        except yaml.YAMLError as e:
            self.logger.error(f"配置文件格式错误: {e}")
            self.config = self._get_default_config()
        except Exception as e:
            self.logger.error(f"加载配置文件失败: {e}")
            self.config = self._get_default_config()
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值（支持嵌套键）
        
        Args:
            key_path: 配置键路径，如 'algorithm.max_turns'
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        设置配置值（支持嵌套键）
        
        Args:
            key_path: 配置键路径
            value: 配置值
        """
        keys = key_path.split('.')
        config = self.config
        
        # 创建嵌套字典结构
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置最终值
        config[keys[-1]] = value
    
    def save_config(self, output_path: Optional[str] = None) -> None:
        """
        保存配置到文件
        
        Args:
            output_path: 输出文件路径，默认为原配置文件路径
        """
        save_path = Path(output_path) if output_path else self.config_path
        
        try:
            # 确保目录存在
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, 
                         allow_unicode=True, indent=2)
            
            self.logger.info(f"配置文件保存成功: {save_path}")
            
        except Exception as e:
            self.logger.error(f"保存配置文件失败: {e}")
    
    def update_from_env(self) -> None:
        """
        从环境变量更新配置
        """
        env_mappings = {
            'TEMPEST_MAX_TURNS': 'algorithm.max_turns',
            'TEMPEST_BRANCH_FACTOR': 'algorithm.branch_factor',
            'TEMPEST_KEEP_BRANCHES': 'algorithm.keep_branches',
            'TEMPEST_LOG_LEVEL': 'logging.level',
            'TEMPEST_RESULTS_DIR': 'output.results_dir',
            'TEMPEST_TIMEOUT': 'api.timeout',
            'TEMPEST_MAX_RETRIES': 'api.max_retries',
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # 尝试转换数据类型
                try:
                    # 尝试转换为整数
                    if env_value.isdigit():
                        env_value = int(env_value)
                    # 尝试转换为浮点数
                    elif '.' in env_value and env_value.replace('.', '').isdigit():
                        env_value = float(env_value)
                    # 尝试转换为布尔值
                    elif env_value.lower() in ['true', 'false']:
                        env_value = env_value.lower() == 'true'
                except ValueError:
                    pass  # 保持字符串类型
                
                self.set(config_key, env_value)
                self.logger.info(f"从环境变量更新配置: {config_key} = {env_value}")
    
    def get_api_config(self, api_name: str) -> Dict[str, Any]:
        """
        获取特定API的配置
        
        Args:
            api_name: API名称 (deepseek, gemini, glm)
            
        Returns:
            API配置字典
        """
        base_config = self.get('api', {})
        api_config = self.get(f'api.{api_name}', {})
        
        # 合并基础配置和特定API配置
        merged_config = {
            'timeout': base_config.get('timeout', 300),
            'max_retries': base_config.get('max_retries', 3),
            'retry_delay': base_config.get('retry_delay', 1),
        }
        merged_config.update(api_config)
        
        return merged_config
    
    def get_algorithm_config(self) -> Dict[str, Any]:
        """
        获取算法配置
        
        Returns:
            算法配置字典
        """
        return self.get('algorithm', self._get_default_algorithm_config())
    
    def get_logging_config(self) -> Dict[str, Any]:
        """
        获取日志配置
        
        Returns:
            日志配置字典
        """
        return self.get('logging', self._get_default_logging_config())
    
    def get_output_config(self) -> Dict[str, Any]:
        """
        获取输出配置
        
        Returns:
            输出配置字典
        """
        return self.get('output', self._get_default_output_config())
    
    def validate_config(self) -> bool:
        """
        验证配置的有效性
        
        Returns:
            配置是否有效
        """
        try:
            # 验证算法参数
            algo_config = self.get_algorithm_config()
            assert algo_config['max_turns'] > 0, "max_turns必须大于0"
            assert algo_config['branch_factor'] > 0, "branch_factor必须大于0"
            assert algo_config['keep_branches'] > 0, "keep_branches必须大于0"
            assert algo_config['keep_branches'] <= algo_config['branch_factor'], \
                "keep_branches不能大于branch_factor"
            
            # 验证API配置
            api_config = self.get('api', {})
            assert api_config.get('timeout', 300) > 0, "timeout必须大于0"
            assert api_config.get('max_retries', 3) >= 0, "max_retries不能为负数"
            
            # 验证日志级别
            log_level = self.get('logging.level', 'INFO')
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            assert log_level in valid_levels, f"日志级别必须是: {valid_levels}"
            
            self.logger.info("配置验证通过")
            return True
            
        except AssertionError as e:
            self.logger.error(f"配置验证失败: {e}")
            return False
        except Exception as e:
            self.logger.error(f"配置验证出错: {e}")
            return False
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'algorithm': self._get_default_algorithm_config(),
            'api': self._get_default_api_config(),
            'logging': self._get_default_logging_config(),
            'output': self._get_default_output_config(),
        }
    
    def _get_default_algorithm_config(self) -> Dict[str, Any]:
        """获取默认算法配置"""
        return {
            'max_turns': 5,
            'branch_factor': 3,
            'keep_branches': 3,
            'success_threshold': 10,
            'partial_threshold': 5,
        }
    
    def _get_default_api_config(self) -> Dict[str, Any]:
        """获取默认API配置"""
        return {
            'timeout': 300,
            'max_retries': 3,
            'retry_delay': 1,
            'max_concurrent_requests': 5,
            'deepseek': {
                'model': 'deepseek-chat',
                'temperature': 0.8,
                'max_tokens': 2048,
            },
            'gemini': {
                'model': 'gemini-pro',
                'temperature': 0.3,
                'max_tokens': 2048,
            },
            'glm': {
                'model': 'glm-4',
                'temperature': 0.5,
                'max_tokens': 2048,
            },
        }
    
    def _get_default_logging_config(self) -> Dict[str, Any]:
        """获取默认日志配置"""
        return {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'file': 'logs/tempest.log',
        }
    
    def _get_default_output_config(self) -> Dict[str, Any]:
        """获取默认输出配置"""
        return {
            'results_dir': 'results',
            'save_conversations': True,
            'save_attack_logs': True,
            'save_statistics': True,
            'export_format': 'json',
        }
    
    def print_config(self) -> None:
        """打印当前配置"""
        print("=== Tempest Framework 配置 ===")
        print(yaml.dump(self.config, default_flow_style=False, 
                       allow_unicode=True, indent=2))


def setup_logging(config_loader: ConfigLoader) -> None:
    """
    根据配置设置日志
    
    Args:
        config_loader: 配置加载器实例
    """
    log_config = config_loader.get_logging_config()
    
    # 创建日志目录
    log_file = log_config.get('file', 'logs/tempest.log')
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_config.get('level', 'INFO')),
        format=log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


if __name__ == "__main__":
    # 测试配置加载器
    config = ConfigLoader()
    
    # 验证配置
    if config.validate_config():
        print("✅ 配置验证通过")
    else:
        print("❌ 配置验证失败")
    
    # 打印配置
    config.print_config()
    
    # 测试环境变量更新
    os.environ['TEMPEST_MAX_TURNS'] = '10'
    config.update_from_env()
    print(f"\n更新后的max_turns: {config.get('algorithm.max_turns')}")
    
    # 设置日志
    setup_logging(config)
    logger = logging.getLogger('test')
    logger.info("配置加载器测试完成")