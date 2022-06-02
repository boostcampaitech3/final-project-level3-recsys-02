import logging


class Logger:
    # file log
    def __init__(self, logPath):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.ERROR)
        formatter = logging.Formatter('[%(asctime)s]: %(message)s\n')
        fileHandler = logging.FileHandler(f'{logPath}', encoding='utf-8')
        fileHandler.setFormatter(formatter)
        self.logger.addHandler(fileHandler)