"""
日志配置模块
配置日志系统，输出到stdout（符合Docker标准）
"""
import logging
import sys


def setup_logger(log_level: str = "INFO"):
    """配置日志系统"""
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level))

    # 清除已有处理器
    logger.handlers.clear()

    # 日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 控制台处理器（stdout，Docker标准）
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
