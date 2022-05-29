import asyncio
from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates
import hashlib
from modules.broker import Broker
from modules.events import ServerLog
import time

# Rate Limiting for QOS
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

"""
slowapi => Throttling (rate limit 설정) 요청 수 제한을 위해 in-memory storage 에 요청을 캐싱하는 구현체
rate limits string format
[count] [per|/] [n (optional)] [second|minute|hour|day|month|year]
출처 : "https://limits.readthedocs.io/en/stable/quickstart.html#rate-limit-string-notation"
"""

# global
HOST = '192.168.1.101:30042'  # Kubernetes Service IP for the broker
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
templates = Jinja2Templates(directory='templates')
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger = ServerLog()
broker = Broker(HOST, logger)

# subjects for debugging only
testSubjects = [
    'input',
]


async def getResult(key: str, timeout: float, interval: float) -> object:
    timeElapsed = 0.0
    timeStarted = time.perf_counter()
    while timeElapsed <= timeout:
        result = await broker.fetchResult(key)
        if result:
            await broker.removeKey(key)
            return result
        timeElapsed += (time.perf_counter() - timeStarted)
        await asyncio.sleep(interval)
    await broker.removeKey(key)
    return None


async def clientBasedHashing(request: Request):
    if request is not None:
        client = str(dict(request)['client']).encode()
        payload = await request.body()
        key = hashlib.sha256(client + payload).hexdigest()
        return payload, key


@app.on_event('startup')
async def init():
    await broker.connect()
    # await broker.removeStream('inference')
    await broker.createStream('inference', testSubjects)
    await broker.createBucket('inference')


@app.get('/')
@limiter.limit('3/second')
async def main(request: Request):
    return templates.TemplateResponse('map.html', {'request': request})


@app.post('/inference')
@limiter.limit('3/second')
async def inference(request: Request):
    payload, key = await clientBasedHashing(request)
    ack = await broker.publish('input', payload, 5.0, 'inference', {'key': key})
    if ack:
        result = await getResult(key, 2.0, 0.5)
        if result:
            return {'status': True, 'data': result}
        else:
            return {'status': False, 'data': 'Unable to fetch the result.'}
    else:
        return {'status': False, 'data': 'Timed out on publishing a message.'}
