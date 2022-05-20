from fastapi import FastAPI
from fastapi import Request
from modules.broker import Broker
from modules.events import Generator, ServerLog

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


async def sayHello():
    return 'hello, world!'


@app.get('/')
@limiter.limit('3/second')
async def root(request: Request):
    return EventSourceResponse(Generator.timeBound(5.0, 1.0, sayHello))


@app.on_event('startup')
async def init():
    await broker.connect()
    await broker.createStream('inference', ['pub', 'sub'])


@app.post('/inference/place_v1')
@limiter.limit('3/second')
async def requestInference(request: Request):
    # return EventSourceResponse()
    return {}
