"""ClipFlow日志模块 - 支持文件和控制台双输出"""

import os
import sys
import logging
import tempfile
from datetime import datetime
from pathlib import Path


class LogManager:
    """日志管理器"""
    
    _instance = None
    _log_file = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_logger()
        return cls._instance
    
    def _init_logger(self):
        """初始化日志系统"""
        # 创建日志目录
        log_dir = os.path.join(tempfile.gettempdir(), 'ClipFlow', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成以时间戳命名的日志文件
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self._log_file = os.path.join(log_dir, f'clipflow_{timestamp}.log')
        
        # 配置logging
        self._logger = logging.getLogger('ClipFlow')
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers = []  # 清空已有handlers
        
        # 文件handler
        file_handler = logging.FileHandler(self._log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self._logger.addHandler(file_handler)
        
        # 同时输出到控制台（用于开发调试）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self._logger.addHandler(console_handler)
        
        self._logger.info(f"日志文件: {self._log_file}")
    
    @property
    def log_file(self):
        """获取当前日志文件路径"""
        return self._log_file
    
    def debug(self, msg):
        self._logger.debug(msg)
    
    def info(self, msg):
        self._logger.info(msg)
    
    def warning(self, msg):
        self._logger.warning(msg)
    
    def error(self, msg):
        self._logger.error(msg)
    
    def critical(self, msg):
        self._logger.critical(msg)


# 全局日志实例
log_manager = LogManager()


def get_log_file():
    """获取当前日志文件路径"""
    return log_manager.log_file


def log_debug(msg):
    log_manager.debug(msg)


def log_info(msg):
    log_manager.info(msg)


def log_warning(msg):
    log_manager.warning(msg)


def log_error(msg):
    log_manager.error(msg)


def log_critical(msg):
    log_manager.critical(msg)