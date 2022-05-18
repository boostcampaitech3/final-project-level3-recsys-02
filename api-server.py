import asyncio
from fastapi import FastAPI
from modules.broker import Broker
from modules import orm


app = FastAPI()
HOST = '192.168.1.101:30042'  # Kubernetes Service IP for the broker
broker = Broker(HOST)


@app.on_event('startup')
async def init():
    status, log = await broker.connect('api-server', 'test-stream', 'test-subject')
    print(status, log)


@app.post('/request')
async def request(data: orm.UserRequest):
    ack = await broker.publish('test-subject', data.dict(), 5.0, 'test-stream', {})
    return {'response': (300, 2)}
