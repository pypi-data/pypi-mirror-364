import logging
import logging.handlers
import os
import time

basedir = os.getcwd()


class Log(object):
    """
    logging的初始化操作，以类封装的形式进行
    """

    def __init__(
        self,
        name,
        enable_file: bool = True,
        lever=logging.DEBUG,
        enable_console: bool = True,
    ):
        # 定义对应的程序模块名name，默认为root
        self.logger = logging.Logger(name)

        # 设置输出的等级
        LEVELS = {
            "NOSET": logging.NOTSET,
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        # 必须设置，这里如果不显示设置，默认过滤掉warning之前的所有级别的信息
        self.logger.setLevel(lever)
        # 日志输出格式
        self.formatter = logging.Formatter("[%(name)s] [%(levelname)s]:%(message)s")
        # log_path是存放日志的路径
        if enable_file:
            time_str = time.strftime("%Y_%m_%d", time.localtime(time.time()))
            lib_path = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "../../logs")
            )
            # 如果不存在这个logs文件夹，就自动创建一个
            if not os.path.exists(lib_path):
                os.mkdir(lib_path)
            # 日志文件的地址
            self.logname = lib_path + "/" + time_str + ".log"
            self.fh = logging.handlers.RotatingFileHandler(
                filename=self.logname,
                maxBytes=1024 * 1024 * 50,
                backupCount=5,
                encoding="utf-8",
            )
            # 设置日志等级
            self.fh.setLevel(logging.DEBUG)
            # 设置handler的格式对象
            self.fh.setFormatter(self.formatter)
            # 将handler增加到logger中
            self.logger.addHandler(self.fh)
            self.fh.close()

        # 创建一个FileHandler， 向文件logname输出日志信息
        # 创建一个StreamHandler,用于输出到控制台
        if enable_console:
            self.ch = logging.StreamHandler()
            self.ch.setLevel(logging.DEBUG)
            self.ch.setFormatter(self.formatter)
            self.logger.addHandler(self.ch)
        # # 关闭打开的文件

    def close(self):

        self.logger.removeHandler(self.fh)

    def info(self, message, *args, **kwargs):
        self.logger.info(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        self.logger.debug(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        self.logger.warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        self.logger.error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        self.logger.critical(message, *args, **kwargs)


def newLog(name: str, enable_file: bool = False, enable_console: bool = True) -> Log:
    return Log(
        name,
        enable_file=enable_file,
        enable_console=enable_console,
        lever=logging.INFO,
    )
