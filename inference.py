import argparse
import asyncio
import json
from modules.broker import Broker
from modules.events import ServerLog
import random


async def main(kwargs: argparse.Namespace):
    logger = ServerLog()
    broker = Broker(kwargs.host, logger)
    await broker.connect()
    await broker.subscribe(kwargs.durable, kwargs.stream, kwargs.subject)
    await broker.createBucket('test')

    while True:
        try:
            batch = await broker.pull(kwargs.batch, timeout=0.5)

            """
            여기 inference logic 넣어주세요.
            아래 if batch 이하 코드는 echo return 입니다.
            """

            if batch:
                for headers, data in batch:
                    key = headers.get('key')
                    payload = {}

                    for index in range(10):
                        placeInfo = {
                            'name': str(index),
                            'latitude': data['latitude'] + random.uniform(-0.001, 0.001),
                            'longitude': data['longitude'] + random.uniform(-0.001, 0.001),
                        }
                        payload[index] = placeInfo
                    data = json.dumps(payload, ensure_ascii=False).encode()
                    await broker.createKey(key=key, value=data)
        except:
            import traceback
            print(traceback.format_exc())


if __name__ == '__main__':
    """
    --host => IP:Port
    --durable => 본인 id (inference server 별로 겹치지 않게)
    --stream => stream 이름
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
