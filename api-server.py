from fastapi import FastAPI
from modules.broker import Broker
from modules import orm

app = FastAPI()
HOST = '10.106.59.62:4222'  # Kubernetes Service IP
broker = Broker(HOST)


@app.get('/ready')
async def root():
    return await broker.connect()


@app.post('/UserRequest')
async def request(data: orm.UserRequest):
    ack = await broker.publish('test-subject', data.dict(), 5.0, 'test-stream', {})
    return ack
