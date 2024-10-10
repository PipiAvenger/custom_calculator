import os
import logging

def ensure_file_exists(file_path):
    """
    确保给定的文件路径存在，如果不存在则创建对应的目录和文件。

    :param file_path: 绝对路径，包括文件名
    """
    logger = logging.getLogger()
    # 获取文件的目录
    file_path = os.path.normpath(file_path)
    directory = os.path.dirname(file_path)

    # 如果目录不存在，则创建目录
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.debug(f"创建目录: {directory}")

    # 如果文件不存在，则创建空文件
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as f:
            pass  # 创建空文件
        logger.debug(f"创建文件: {file_path}")
