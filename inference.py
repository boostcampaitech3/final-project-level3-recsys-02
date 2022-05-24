import argparse
import asyncio
import json
from modules.broker import Broker
from modules.events import ServerLog
import pickle


async def main(kwargs):
    logger = ServerLog()
    broker = Broker(kwargs.host, logger)
    await broker.connect()
    await broker.subscribe(kwargs.durable, kwargs.stream, kwargs.subject)
    await broker.createBucket('inference')

    """
    Model 인스턴스 여기에 생성해주세요.
    """

    while True:
        try:
            batch = await broker.pull(kwargs.batch)

            """
            여기 inference logic 넣어주세요.
            아래 if batch 이하 코드는 echo return 입니다.
            """

            if batch:
                for headers, data in batch:
                    await broker.createKey(key=headers['key'], value=json.dumps(data).encode())
        except:
            import traceback
            print(traceback.format_exc())


if __name__ == '__main__':
    """
    --host => IP:Port
    --durable => 본인 id (inference server 별로 겹치지 않게)
    --stream => stream 이름
    --key => key 이름
    --batch => 배치 사이즈 (기본 : 100)
    """
    config = argparse.ArgumentParser(description='How to run an Inference Server')
    config.add_argument('--host', type=str, required=True, help='host "IP:port" formatted string')
    config.add_argument('--durable', type=str, required=True, help='an inference server identifier')
    config.add_argument('--stream', type=str, required=True, help='a stream name')
    config.add_argument('--subject', type=str, required=True, help='a subject name to subscribe to')
    config.add_argument('--batch', default=100, type=int, help='determine a batch size to be inferred at a time')
    args = config.parse_args()
    asyncio.run(main(args))
