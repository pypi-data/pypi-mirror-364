import logging
import sys
from datetime import datetime
from pathlib import Path


class LogUtil:
    """
    日志工具类，提供同时输出到控制台和文件的功能
    日志文件按天生成，存储在项目根目录的logs目录下
    """
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name='getDialog', level=logging.INFO):
        """
        获取日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
            
        Returns:
            logging.Logger: 配置好的日志记录器
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(level)
        
        # 清除已有的处理器
        logger.handlers.clear()
        
        # 创建格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # 文件处理器
        file_handler = cls._create_file_handler(level, formatter)
        logger.addHandler(file_handler)
        
        # 避免重复日志
        logger.propagate = False
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def _create_file_handler(cls, level, formatter):
        """
        创建文件处理器
        
        Args:
            level: 日志级别
            formatter: 格式化器
            
        Returns:
            logging.FileHandler: 文件处理器
        """
        # 获取项目根目录
        project_root = Path(__file__).parent.parent.parent.parent
        logs_dir = project_root / 'logs'
        
        # 确保日志目录存在
        logs_dir.mkdir(exist_ok=True)
        
        # 生成日志文件名（按天）
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = logs_dir / f'getDialog_{today}.log'
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        return file_handler
    
    @classmethod
    def info(cls, message, logger_name='getDialog'):
        """记录INFO级别日志"""
        logger = cls.get_logger(logger_name)
        logger.info(message)
    
    @classmethod
    def debug(cls, message, logger_name='getDialog'):
        """记录DEBUG级别日志"""
        logger = cls.get_logger(logger_name)
        logger.debug(message)
    
    @classmethod
    def warning(cls, message, logger_name='getDialog'):
        """记录WARNING级别日志"""
        logger = cls.get_logger(logger_name)
        logger.warning(message)
    
    @classmethod
    def error(cls, message, logger_name='getDialog'):
        """记录ERROR级别日志"""
        logger = cls.get_logger(logger_name)
        logger.error(message)
    
    @classmethod
    def critical(cls, message, logger_name='getDialog'):
        """记录CRITICAL级别日志"""
        logger = cls.get_logger(logger_name)
        logger.critical(message)


# 提供默认实例
default_logger = LogUtil.get_logger()


def log_info(message):
    """快捷方法：记录INFO级别日志"""
    default_logger.info(message)


def log_debug(message):
    """快捷方法：记录DEBUG级别日志"""
    default_logger.debug(message)


def log_warning(message):
    """快捷方法：记录WARNING级别日志"""
    default_logger.warning(message)


def log_error(message):
    """快捷方法：记录ERROR级别日志"""
    default_logger.error(message)


def log_critical(message):
    """快捷方法：记录CRITICAL级别日志"""
    default_logger.critical(message)