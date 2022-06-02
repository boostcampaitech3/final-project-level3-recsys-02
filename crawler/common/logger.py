import logging


class Logger:
    # file log
    def __init__(self, logPath, appname):
        self.logger = logging.getLogger(appname)
        self.logger.propagate = False
        self.logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('[%(asctime)s]: %(message)s\n')
        fileHandler = logging.FileHandler(f'{logPath}', encoding='utf-8')
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)