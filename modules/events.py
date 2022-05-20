import asyncio
from datetime import datetime
import time
from typing import Callable


class Generator:
    @staticmethod
    async def timeBound(timeout: float, interval: float, function: Callable):
        timeElapsed = 0.0
        timeStarted = time.perf_counter()
        while timeElapsed < timeout:
            await asyncio.sleep(interval)
            timeElapsed = time.perf_counter() - timeStarted
            yield await function()

    @staticmethod
    async def iterBound(iterations: int, interval: float, function: Callable):
        for rep in range(iterations):
            await asyncio.sleep(interval)
            yield await function()


class ServerLog:
    @staticmethod
    def formatter(message: str):
        """
        Pod console 에 메시지 표시할 때 포맷해주는 wrapper function
        :param message: log string
        :return:
        """
        formatted = datetime.now().strftime('[%Y/%D, %H:%M:%S] : {log}').format(log=message)
        print(formatted)
        return formatted
