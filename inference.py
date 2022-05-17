import argparse
import asyncio
from modules.broker import Broker
from models.skeleton import RandomRec


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
    broker = Broker(host)
    status, log = await broker.connect('testServer', 'test-stream', 'test-subject')
    if status is False:
        return status, log
    print(log)

    model = RandomRec()
    while True:
        try:
            batch = await broker.pull(batchSize)
            """
            feed forward
            """
            results = model.forward(batch)
            ack = await broker.publish('test-subject', results, 5.0, 'test-stream', {})
            print(ack)
            await asyncio.sleep(0.5)
        except:
            pass


if __name__ == '__main__':
    config = argparse.ArgumentParser(description='How to run an Inference Server')
    config.add_argument('--host', type=str, required=True, help='host "IP:port" formatted string')
    config.add_argument('--batch-size', default=100, type=int, help='determine a batch size to be inferred at a time')
    args = config.parse_args()
    status, log = asyncio.run(main(args.host, args.batch_size))
    print(log)
