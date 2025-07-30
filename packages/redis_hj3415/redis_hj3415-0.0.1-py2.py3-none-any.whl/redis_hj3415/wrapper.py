import hashlib

from typing import Any, Callable, Awaitable
import json, os, redis, functools, inspect

from .common.connection import get_redis_client, get_redis_client_async


from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'INFO')


def _make_key(tickers: list[str], trend: str) -> str:
    """티커 리스트 + 트렌드 → 해시 16자 키

    Args:
        tickers: 종목 코드 목록
        trend  : "up"/"down" 등 트렌드 문자열

    Returns:
        예) "up:9b1de34a98c2a1f0"
    """
    norm = sorted(set(t.lower() for t in tickers))       # 정렬·중복 제거
    sha1 = hashlib.sha1(",".join(norm).encode()).hexdigest()[:16]
    return f"{trend}:{sha1}"                             # 짧고 충돌 낮음


def redis_cached(prefix: str | None = None, default_if_miss=None):
    """함수 결과를 Redis에 캐싱하는 데코레이터

    Parameters
    ----------
    prefix : str | None
        Redis 키 프리픽스. 기본값은 래핑되는 함수 이름.
    default_if_miss : Any | Callable[[], Any] | None
        캐시 미스(`cache_only=True`) 시 즉시 반환할 기본값<br>
        함수를 넘기면 지연 평가(lazy)됩니다.

    Keyword Args 전용
    ---------------
    refresh : bool, default False
        `True`면 캐시를 무시하고 원본 함수를 실행한 뒤 값을 재작성.
    cache_only : bool, default False
        `True`면 캐시가 없을 때 원본 함수를 **호출하지 않고**
        `default_if_miss`를 반환.

    Returns
    -------
    Callable
        캐싱이 적용된 동일 시그니처의 함수.

    Example
    -------
    ```python
    @redis_cached(prefix="trend", default_if_miss={})
    def get_trend(ticker: str, days: int) -> dict: ...
    ```
    """
    ttl_h = int(os.getenv("REDIS_EXPIRE_TIME_H", 12))
    prefix = prefix  # 나중에 wraps 안에서 참조

    def decorator(func):
        cache_prefix = prefix or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            refresh: bool = kwargs.pop("refresh", False)
            cache_only: bool = kwargs.pop("cache_only", False)

            redis_cli = get_redis_client()

            if isinstance(args[0], list):  # tickers 리스트인 경우
                key_suffix = _make_key(args[0], args[1])  # trend = args[1]
            else:  # 단일 ticker
                key_suffix = str(args[0]).lower()
            cache_key = f"{cache_prefix}:{key_suffix}"

            ttl = ttl_h * 60 * 60

            # ── 1) 캐시 조회 (refresh=False일 때만) ───────────
            if not refresh:
                try:
                    raw = redis_cli.get(cache_key)
                    if raw is not None:
                        mylogger.info(f"cache hit {cache_key}")
                        return json.loads(raw)
                except redis.RedisError as e:
                    mylogger.warning(f"Redis GET fail: {e}")

            # ── 2) cache_only 처리 ────────────────────────
            if cache_only and not refresh:
                mylogger.info(f"cache miss {cache_key} → 기본값 반환")
                return default_if_miss

            # ── 3) 원본 함수 실행 & 캐시 갱신 ──────────
            mylogger.info(
                f"{cache_key} → 계산 후 캐시{' 갱신' if refresh else ' 저장'}"
            )
            result = func(*args, **kwargs)

            try:
                redis_cli.setex(cache_key, ttl, json.dumps(result))
                mylogger.info(f"[redis] SETEX {cache_key} ({ttl}s)")
            except redis.RedisError as e:
                mylogger.warning(f"Redis SETEX fail: {e}")
            return result

        return wrapper
    return decorator


def redis_async_cached(
    prefix: str | None = None,
    default_if_miss: Any = None,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """
    비동기 함수(async def)에만 붙일 수 있는 Redis 캐싱 데코레이터.

    Parameters
    ----------
    prefix : str | None
        Redis 키 prefix. 생략하면 함수 이름을 사용.
    default_if_miss : Any
        cache_only=True 이고 캐시가 없을 때 반환할 기본값.

    사용 예
    -------
    @redis_async_cached(prefix="prophet")
    async def prophet_forecast(...):
        ...
    """
    ttl_h = int(os.getenv("REDIS_EXPIRE_TIME_H", 12))
    ttl   = ttl_h * 60 * 60

    def decorator(func: Callable[..., Awaitable[Any]]):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("redis_async_cached 는 async 함수에만 사용할 수 있습니다.")

        cache_prefix = prefix or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            refresh: bool = kwargs.pop("refresh", False)
            cache_only: bool = kwargs.pop("cache_only", False)

            redis_cli = get_redis_client_async()

            if isinstance(args[0], list):  # tickers 리스트인 경우
                key_suffix = _make_key(args[0], args[1])  # trend = args[1]
            else:  # 단일 ticker
                key_suffix = str(args[0]).lower()
            cache_key = f"{cache_prefix}:{key_suffix}"

            # 1) 캐시 조회
            if not refresh:
                try:
                    raw = await redis_cli.get(cache_key)
                    if raw is not None:
                        mylogger.info(f"[redis] HIT  {cache_key}")
                        return json.loads(raw)
                except Exception as e:
                    mylogger.warning(f"[redis] GET 실패: {e}")

            # 2) cache_only 처리
            if cache_only and not refresh:
                mylogger.info(f"[redis] MISS {cache_key} → 기본값 반환")
                return default_if_miss

            # 3) 원본 함수 실행
            mylogger.info(f"[redis] RUN  {cache_key} (refresh={refresh})")
            result = await func(*args, **kwargs)

            # 4) 캐시 갱신
            try:
                await redis_cli.setex(cache_key, ttl, json.dumps(result))
                mylogger.info(f"[redis] SETEX {cache_key} ({ttl}s)")
            except Exception as e:
                mylogger.warning(f"[redis] SETEX 실패: {e}")

            return result

        return wrapper

    return decorator
