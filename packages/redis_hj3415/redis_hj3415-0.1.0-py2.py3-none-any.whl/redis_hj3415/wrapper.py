import hashlib
import functools
import inspect
import json
import os
import random
import redis
from typing import Any, Callable, Awaitable, TypeVar

from pydantic import BaseModel
from pydantic_core import to_jsonable_python  # pydantic v2 권장

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



M = TypeVar("M", bound=BaseModel)

def _json_default(o: Any):
    # datetime/Decimal/UUID/set 등 방어적 직렬화
    try:
        return to_jsonable_python(o)
    except Exception:
        return str(o)

def _safe_cache_key(cache_prefix: str, args: tuple, kwargs: dict) -> str:
    """
    args[0], args[1] 전제에 의존하지 않고 안전하게 키를 생성.
    needed: 동일 함수 동일 인자 → 동일 키
    """
    # 가볍게: 위치/키워드 인자 문자열화 후 해시
    try:
        from hashlib import sha1
        payload = json.dumps(
            {
                "args": args,
                "kwargs": kwargs,
            },
            default=str,
            ensure_ascii=False,
            sort_keys=True,
        )
        digest = sha1(payload.encode("utf-8")).hexdigest()[:16]
        return f"{cache_prefix}:{digest}"
    except Exception:
        # 최후의 방어: 단순 repr
        return f"{cache_prefix}:{repr((args, kwargs))}"

def redis_async_cached_model(
    model: type[M],
    *,
    prefix: str | None = None,
    default_if_miss: Any = None,
):
    """
    Pydantic 모델(M) 또는 모델 리스트(list[M])을 반환하는 비동기 함수용 Redis 캐시 데코레이터.

    - 캐시 HIT 시: 저장 당시와 동일한 구조(단일 모델 or 리스트)로 복원.
    - 캐시 MISS 시: 원본 함수 실행 후 JSON 저장.
    - `refresh=True` → 캐시 무시하고 원본 실행 후 갱신(= refresh 우선).
    - `cache_only=True` & MISS → `default_if_miss` 반환.
    """
    ttl_h = int(os.getenv("REDIS_EXPIRE_TIME_H", 12))
    base_ttl = ttl_h * 60 * 60

    def decorator(func: Callable[..., Awaitable[M] | Awaitable[list[M]]]):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("redis_async_cached_model 데코레이터는 async 함수에만 사용 가능합니다.")

        cache_prefix = prefix or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            refresh: bool = kwargs.pop("refresh", False)
            cache_only: bool = kwargs.pop("cache_only", False)

            redis_cli = get_redis_client_async()  # decode_responses=True 권장

            # ── 키 생성 (안전 버전) ───────────────────────────
            cache_key = _safe_cache_key(cache_prefix, args, kwargs)

            # ── 1) 캐시 조회 ─────────────────────────────────
            if not refresh:
                try:
                    raw = await redis_cli.get(cache_key)
                    if raw is not None:
                        mylogger.info(f"[redis] HIT  {cache_key}")
                        # bytes → str
                        raw_str = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
                        # ① 단일 모델 시도
                        try:
                            return model.model_validate_json(raw_str)  # type: ignore[return-value]
                        except Exception:
                            # ② 리스트 시도
                            data = json.loads(raw_str)
                            if isinstance(data, list):
                                return [model.model_validate(d) for d in data]  # type: ignore[return-value]
                            # ③ 기타: 그대로 반환(혹은 raise)
                            return data  # 필요 시 raise로 바꾸세요.
                except Exception as e:
                    mylogger.warning(f"[redis] GET 실패: {e}")

            # ── 2) cache_only 처리 ───────────────────────────
            if cache_only and not refresh:
                mylogger.info(f"[redis] MISS {cache_key} → 기본값 반환")
                return default_if_miss

            # ── 3) 원본 실행 ─────────────────────────────────
            result = await func(*args, **kwargs)

            # ── 4) 캐시 갱신 ─────────────────────────────────
            try:
                # TTL 지터(±0~300s) → 캐시 스탬피드 완화
                ttl = base_ttl + random.randint(0, 300)

                if isinstance(result, list):
                    if result and isinstance(result[0], BaseModel):
                        payload = json.dumps([m.model_dump(mode="json") for m in result], ensure_ascii=False)
                    else:
                        payload = json.dumps(to_jsonable_python(result), default=_json_default, ensure_ascii=False)
                elif isinstance(result, BaseModel):
                    payload = result.model_dump_json()
                else:
                    payload = json.dumps(to_jsonable_python(result), default=_json_default, ensure_ascii=False)

                await redis_cli.setex(cache_key, ttl, payload)
                mylogger.info(f"[redis] SETEX {cache_key} ({ttl}s)")
            except Exception as e:
                mylogger.warning(f"[redis] SETEX 실패: {e}")

            return result

        return wrapper
    return decorator