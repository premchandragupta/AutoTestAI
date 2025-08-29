
import os, time, asyncio
from starlette.requests import Request
from starlette.responses import JSONResponse
import aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
RATE_LIMIT = int(os.getenv("RATE_LIMIT", "60"))
RATE_PERIOD = int(os.getenv("RATE_PERIOD", "60"))

_redis = None
_lock = asyncio.Lock()

async def _get_redis():
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)
    return _redis

async def limiter_middleware(request: Request, call_next):
    client = "unknown"
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(" ",1)[1]
        try:
            from .auth import decode_access_token
            payload = decode_access_token(token)
            client = f"user:{payload.get('user_id')}"
        except Exception:
            client = "unknown"
    else:
        api_key = request.headers.get("x-api-key") or request.headers.get("X-API-Key")
        if api_key:
            client = f"apikey:{api_key}"
        else:
            client = request.client.host if request.client else "unknown"
    period = int(time.time()) // RATE_PERIOD
    key = f"rl:{client}:{period}"
    try:
        redis = await _get_redis()
        count = await redis.incr(key)
        if count == 1:
            await redis.expire(key, RATE_PERIOD + 1)
        if int(count) > RATE_LIMIT:
            return JSONResponse({"detail":"Rate limit exceeded. Try later."}, status_code=429)
    except Exception:
        # on redis error, allow requests (fail-open)
        pass
    return await call_next(request)
