import asyncio
from fastapi import FastAPI
from fastapi import WebSocket, WebSocketDisconnect
from modules.broker import Broker
from modules.events import Events
from modules import orm


class ConnectionManager:
    """
    웹소켓 connection manager event-driven callbacks 구현체 입니다. 공식 튜토리얼 참고했습니다.
    출처 : 'https://fastapi.tiangolo.com/advanced/websockets/'
    """
    def __init__(self, logger):
        # hard limit set on the uvicorn server
        self.logger = logger
        self.active = []

    async def onConnection(self, websocket: WebSocket):
        self.logger.formatter(websocket)
        self.logger.formatter(await websocket.accept())

    def onDisconnection(self, websocket: WebSocket):
        self.logger.formatter('{client} disconnected.'.format(client=websocket))
        self.active.remove(websocket)

"""
Push server 가 없으므로 웹소켓으로 비슷하게 구현합니다.
connection hard limit 은 처리량을 보고 결정할게요. 
"""

# global
HOST = '192.168.1.101:30042'  # Kubernetes Service IP for the broker
app = FastAPI()
logger = Events()
broker = Broker(HOST, logger)
manager = ConnectionManager(logger)


@app.on_event('startup')
async def init():
    await broker.connect()
    await broker.createStream('inference', ['pub', 'sub'])


@app.websocket('/')
async def createChannel(websocket: WebSocket):
    """
    batch pulling 이 timeout 을 구현하므로 connection hard limit 이 있다면 클라이언트 관리가 가능합니다.
    subject 갯수에 hard limit 이 없지만 connection limit 보다 적게 설계됩니다.
    접속이 끊긴 클라이언트는 ConnectionManager class 에서 관리됩니다.

    :param websocket: WebSocket class
    :return:
    """
    await manager.onConnection(websocket)
    try:
        """
        Needs to be filled here !!!
        """
        pass
    except WebSocketDisconnect:
        manager.onDisconnection(websocket)
