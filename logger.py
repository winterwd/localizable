# coding=utf-8
# logger.py

import logging
import os


def setup_logger(log_file=None):
    # 如果未指定日志文件路径，使用默认路径
    if log_file is None:
        log_file = "./logger.log"

    # 文件路径不存在，则创建
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    # 创建日志记录器
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # 创建文件处理程序
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # 创建格式化程序
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # 将处理程序添加到记录器
    logger.addHandler(file_handler)

    return logger


# 示例用法
if __name__ == "__main__":
    logger = setup_logger()
    logger.info("This is an info message.")
    logger.error("This is an error message.")
