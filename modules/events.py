from datetime import datetime


class Events:
    @staticmethod
    def formatter(message):
        """
        Pod console 에 메시지 표시할 때 포맷해주는 wrapper function
        :param message: log string
        :return:
        """
        print(datetime.now().strftime('[%Y/%D, %H:%M:%S] : {log}').format(log=message))
