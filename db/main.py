"""
Batch Pull Consumer
"""

import asyncio
import nats
from consumer import BatchPullConsumer
from logger import Logger

BATCHSIZE = 10
ERRORLOGER = Logger('D:\\PythonProjects\\L7D\\logs\\errors.txt')
HOST = '192.168.1.101:30042'
PODNAME = 'psub-{index}'  # <-- Statefulset field $metadata.name
STREAM = 'data'
SUBJECTS = ['placeInfo', 'reviewInfo', 'userInfo']


async def main():
    client = await nats.connect(HOST)
    jetstream = client.jetstream()
    # print(await jetstream.delete_stream('data'))
    print(await jetstream.add_stream(name=STREAM, subjects=SUBJECTS))

    subscribers = []
    count = 1
    for topic in SUBJECTS:
        client = BatchPullConsumer(BATCHSIZE, ERRORLOGER)
        await client.connect(HOST, PODNAME.format(index=count), STREAM, [topic])
        subscribers.append(client)
        count += 1

    while True:
        for consumer in subscribers:
            await consumer.read()


if __name__ == '__main__':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
