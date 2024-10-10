import logging
import logging.config
import os
from logging.handlers import RotatingFileHandler
import configparser

class Logger:
    _instance = None

    def __new__(cls, log_file='app.log', log_level=logging.INFO):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.__init__(log_file, log_level)
        return cls._instance

    def __init__(self, config_path=None, log_level=logging.INFO):
        """
        初始化Logger类，支持从配置文件加载配置。如果配置文件不存在，使用默认配置
        :param config_path: 日志配置文件路径（默认为当前目录的config/program.log）
        """
        self.config_path = config_path or os.path.join(os.getcwd(), 'config', 'program.conf')
        self.log_directory = os.path.join(os.getcwd(), 'log')
        self.log_file_path = os.path.join(self.log_directory, 'program.log')
        self.log_level = log_level

        # 如果配置文件不存在，使用默认配置
        if not os.path.exists(self.config_path):
            self._setup_default_logging()
        else:
            self._setup_logging_from_config()

    def _setup_default_logging(self):
        """
        使用默认配置设置日志，输出到控制台和文件，并支持文件滚动
        """
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)

        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(funcName)s]:%(message)s')

        # 创建控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)
        console_handler.setLevel(self.log_level)

        # 创建文件日志处理器，支持文件滚动
        file_handler = RotatingFileHandler(self.log_file_path, maxBytes=100 * 1024 * 1024, backupCount=5, encoding='utf-8')
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(self.log_level)

        # 获取根日志记录器并配置
        logging.basicConfig(level=self.log_level, handlers=[console_handler, file_handler])

        # 设置日志器实例
        self.logger = logging.getLogger()

    def _setup_logging_from_config(self):
        """
        从配置文件设置日志
        """
        config = configparser.ConfigParser()
        config.read(self.config_path)

        # 获取配置文件中的路径设置，默认为点1中的路径
        log_file = config.get('Program', 'log_file', fallback=self.log_file_path)
        log_level = config.get('Program', 'log_level', fallback='DEBUG')
        max_bytes = config.getint('Program', 'max_bytes', fallback=100 * 1024 * 1024)
        backup_count = config.getint('Program', 'backup_count', fallback=5)

        if not os.path.exists(os.path.dirname(log_file)):
            os.makedirs(os.path.dirname(log_file))

        log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(funcName)s]:%(message)s')

        # 创建控制台日志处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_formatter)

        # 创建文件日志处理器，支持文件滚动
        file_handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count, encoding='utf-8')
        file_handler.setFormatter(log_formatter)

        # 获取根日志记录器并配置
        logging.basicConfig(level=getattr(logging, log_level.upper(), logging.DEBUG), handlers=[console_handler, file_handler])

        # 设置日志器实例
        self.logger = logging.getLogger()

    def get_logger(self):
        """
        返回日志实例
        :return: 日志记录器
        """
        return self.logger

    def debug(self, message):
        """记录调试信息"""
        self.logger.debug(message)

    def info(self, message):
        """记录普通信息"""
        self.logger.info(message)

    def warning(self, message):
        """记录警告信息"""
        self.logger.warning(message)

    def error(self, message):
        """记录错误信息"""
        self.logger.error(message)

    def critical(self, message):
        """记录严重错误信息"""
        self.logger.critical(message)

# 初始化日志类
Logger(log_level = logging.DEBUG)


# 使用示例
if __name__ == "__main__":
    logger1 = Logger(log_file='application.log', log_level=logging.DEBUG)
    logger2 = Logger(log_file='another_log.log')  # 尝试创建另一个实例

    logger1.debug("这是调试信息")
    logger1.info("这是普通信息")
    logger2.warning("这是警告信息")  # logger2 实际上是 logger1 的引用
    logger1.error("这是错误信息")
    logger1.critical("这是严重错误信息")

    print(logger1 is logger2)  # 输出 True，表明 logger1 和 logger2 是同一个实例
