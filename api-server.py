import asyncio
from fastapi import FastAPI
from fastapi import Request
from modules.broker import Broker
from modules.events import ServerLog
from modules.orm import UserRequest
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded


"""
sse => Server Side Event 

slowapi => Throttling (rate limit 설정) 요청 수 제한을 구현하기 위해 in-memory storage 에 요청을 캐싱해야 합니다.
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


@app.on_event('startup')
async def init():
    await broker.connect()
    await broker.createStream('inference', ['pub', 'sub'])


@app.post('/inference/pub')
@limiter.limit('3/second')
async def requestInference(request: Request):
    await broker.createStream('inference', [''])
    return {}


@app.get('/inference/sub')
@limiter.limit('3/second')
async def requestResult(request: Request):
    '''
    for key, value in request.headers.items():
        print('{key} | {keyType} : {value} | {valueType}'.format(
            key=key,
            keyType=type(key),
            value=value,
            valueType=type(value),
            )
        )
    '''
    payload = {
        'id': 'abcd',
        'lon': 35.0,
        'lat': 38.0,
    }
    return payload
