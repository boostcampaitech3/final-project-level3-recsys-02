import argparse
import asyncio
from modules.broker import Broker
from modules.events import ServerLog


async def main(
        host: str,
        batchSize: int
) -> tuple:
    """
    배치 inferencing implementation

    :param host: an IP:port formatted string
    :param batchSize: the number of user requests to be inferred
    :return:
    """
    logger = ServerLog()
    broker = Broker(host, logger)
    await broker.connect()

    """
    Model 인스턴스 여기에 생성해주세요.
    """

    while True:
        try:
            batch = await broker.pull(batchSize)
            """
            Model inference 여기에 해주세요.
            """
            await asyncio.sleep(0.5)
        except:
            pass


if __name__ == '__main__':
    config = argparse.ArgumentParser(description='How to run an Inference Server')
    config.add_argument('--host', type=str, required=True, help='host "IP:port" formatted string')
    config.add_argument('--batch-size', default=100, type=int, help='determine a batch size to be inferred at a time')
    args = config.parse_args()
    asyncio.run(main(args.host, args.batch_size))
