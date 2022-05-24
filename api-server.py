import asyncio
from fastapi import FastAPI
from fastapi import Request
import hashlib
from modules.broker import Broker
from modules.events import ServerLog
import time

# Rate Limiting for QOS
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Server Sent Events Implementation
from sse_starlette.sse import EventSourceResponse

"""
sse => Server Side Event
Generator.timeBound | Generator.iterBound 
Both are static wrapper functions

slowapi => Throttling (rate limit 설정) 요청 수 제한을 위해 in-memory storage 에 요청을 캐싱하는 구현체
rate limits string format
[count] [per|/] [n (optional)] [second|minute|hour|day|month|year]
출처 : "https://limits.readthedocs.io/en/stable/quickstart.html#rate-limit-string-notation"
"""

# global
HOST = '192.168.1.101:30042'  # Kubernetes Service IP for the broker
limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
logger = ServerLog()
broker = Broker(HOST, logger)

# subjects for debugging only
testSubjects = [
    'byp-input',
    'djp-input',
    'jyy-input',
    'mjk-input',
    'dhl-input',
]


@app.on_event('startup')
async def init():
    await broker.connect()
    await broker.createStream('inference', testSubjects)
    await broker.createBucket('inference')


async def clientBasedHashing(request: Request):
    if request is not None:
        client = str(dict(request)['client']).encode()
        payload = await request.body()
        key = hashlib.sha256(client + payload).hexdigest()
        return payload, key


async def debug(request: Request, stream, subject, key: str):
    payload = await request.body()
    response = await broker.publish(subject, payload, 5.0, stream, {'key': key})
    if response:
        timeout = 2.0
        timeElapsed = 0.0
        timeStarted = time.perf_counter()
        interval = 0.5
        while timeElapsed <= timeout:
            result = await broker.fetchResult(key)

            # fetch succeeded
            if result is not None:
                await broker.removeKey(key)
                return {'response': result}

            timeElapsed += (time.perf_counter() - timeStarted)
            await asyncio.sleep(interval)
        return {'response': 'Unable to fetch the result'}
    else:
        return {'response': 'Failed to publish due to the server timeout'}


@app.post('/inference/byp')
@limiter.limit('5/second')
async def inference0(request: Request):
    output = await debug(request, 'inference', 'byp-input', 'byp-output')
    return output


@app.post('/inference/djp')
@limiter.limit('5/second')
async def inference1(request: Request):
    output = await debug(request, 'inference', 'djp-input', 'djp-output')
    return output


@app.post('/inference/jyy')
@limiter.limit('5/second')
async def inference2(request: Request):
    output = await debug(request, 'inference', 'jyy-input', 'jyy-output')
    return output


@app.post('/inference/mjk')
@limiter.limit('5/second')
async def inference3(request: Request):
    output = await debug(request, 'inference', 'mjk-input', 'mjk-output')
    return output


@app.post('/inference/dhl')
@limiter.limit('5/second')
async def inference4(request: Request):
    output = await debug(request, 'inference', 'dhl-input', 'dhl-output')
    return output
