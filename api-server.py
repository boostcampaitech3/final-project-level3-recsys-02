import asyncio
from fastapi import BackgroundTasks
from fastapi import FastAPI
from fastapi import WebSocket
from modules.broker import Broker
from modules import orm


class TaskManager:
    def __init__(self, broker):
        self.broker = broker
        self.connections = {}

    async def onConnection(self, websocket: WebSocket):
        await websocket.accept()

    async def run(self):
        while True:
            self.broker.pull()
            await asyncio.sleep(0.1)


app = FastAPI()
HOST = '192.168.1.101:30042'  # Kubernetes Service IP
broker = Broker(HOST)
manager = TaskManager(broker)


@app.on_event('startup')
async def init():
    status, log = await broker.connect('api-server', 'test-stream', 'test-subject')
    print(status, log)


@app.post('/request')
async def request(data: orm.UserRequest):
    ack = await broker.publish('test-subject', data.dict(), 5.0, 'test-stream', {})
    return ack


@app.websocket('/push')
async def push(websocket: WebSocket):
    await manager.onConnection(websocket)
