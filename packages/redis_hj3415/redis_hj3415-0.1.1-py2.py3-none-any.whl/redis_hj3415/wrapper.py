import hashlib
import functools
import inspect
import json
import os
import random
from datetime import timedelta

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

def _json_default(o: Any):
    try:
        return to_jsonable_python(o)
    except Exception:
        return str(o)

def _seconds_from_ttl(ttl: Any) -> int | None:
    """int(초), timedelta, None / 잘못된 값이면 None."""
    if ttl is None:
        return None
    if isinstance(ttl, timedelta):
        return int(ttl.total_seconds())
    try:
        val = int(ttl)
        return val
    except Exception:
        return None

def _apply_jitter(base_ttl: int, jitter: int | tuple[int, int] | None) -> int:
    """지터 범위를 base_ttl에 더함."""
    if not jitter:
        return base_ttl
    if isinstance(jitter, tuple):
        lo, hi = jitter
        if hi <= 0:
            return base_ttl
        return base_ttl + random.randint(max(0, lo), hi)
    # int
    if jitter <= 0:
        return base_ttl
    return base_ttl + random.randint(0, jitter)

def _safe_cache_key(cache_prefix: str, args: tuple, kwargs: dict) -> str:
    """호출 인자를 해시해서 안전한 캐시 키 생성."""
    from hashlib import sha1
    payload = json.dumps(
        {"args": args, "kwargs": kwargs},
        default=str, ensure_ascii=False, sort_keys=True,
    )
    digest = sha1(payload.encode("utf-8")).hexdigest()[:16]
    return f"{cache_prefix}:{digest}"


def redis_cached(
    *,
    prefix: str | None = None,
    default_if_miss: Any = None,
    ttl: int | timedelta | None = None,                   # ⬅️ 데코레이터 인자: 기본 TTL(초 또는 timedelta)
    jitter: int | tuple[int, int] | None = 300,           # ⬅️ 스탬피드 완화용 지터(초). 0/None이면 미적용
    ttl_kwarg: str = "cache_ttl",                         # ⬅️ 호출 시점 TTL 덮어쓰기 키워드 인자 이름
    key_factory: Callable[[tuple, dict, str], str] | None = None,  # ⬅️ 캐시 키 커스터마이저(선택)
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    동기 함수 결과를 Redis에 캐싱하는 데코레이터.

    Parameters
    ----------
    prefix : str | None
        Redis 키 prefix. 생략하면 함수 이름을 사용.
    default_if_miss : Any
        `cache_only=True`이고 캐시 미스일 때 반환할 기본값.
        함수(Callable)를 넘기면 지연 평가(lazy)됩니다.
    ttl : int | timedelta | None
        기본 TTL(초). None이면 환경변수 REDIS_EXPIRE_TIME_H(시간)로부터 계산.
        0 또는 음수면 저장을 생략(캐시하지 않음).
    jitter : int | (int,int) | None
        TTL에 추가할 난수(초). int면 [0, jitter], tuple이면 [lo, hi].
        0/None이면 지터 미적용.
    ttl_kwarg : str
        호출 시점에서 `fn(..., cache_ttl=5)`처럼 TTL을 덮어쓸 때 사용할 키워드 인자명.
    key_factory : Callable[(args, kwargs, cache_prefix) -> str]
        캐시 키 생성 로직을 커스터마이즈하고 싶을 때 사용.
        기본값(None)일 경우 `_safe_cache_key(cache_prefix, args, kwargs)` 사용.

    호출 시 지원되는 특수 kwargs
    --------------------------
    refresh : bool = False
        True면 캐시를 무시하고 원본 함수를 실행한 뒤 갱신.
    cache_only : bool = False
        True이고 MISS면 원본 함수를 실행하지 않고 default_if_miss 반환.
    {ttl_kwarg} : int | timedelta | None
        이 호출에 한해 TTL 덮어쓰기.

    동작
    ----
    - 캐시 HIT : json.loads로 역직렬화해 반환(파이썬 기본 타입).
    - 캐시 MISS : 원본 실행 후 JSON 저장(직렬화 불가 타입은 to_jsonable_python + _json_default로 처리).
    """
    # 환경 변수(시간) → 초
    env_hours = int(os.getenv("REDIS_EXPIRE_TIME_H", 12))
    env_default_ttl = env_hours * 60 * 60

    # 데코레이터 레벨 기본 TTL을 초 단위로 정규화
    decorator_base_ttl = _seconds_from_ttl(ttl)
    if decorator_base_ttl is None:
        decorator_base_ttl = env_default_ttl

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        cache_prefix = prefix or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            refresh: bool = kwargs.pop("refresh", False)
            cache_only: bool = kwargs.pop("cache_only", False)

            # 호출 시점 TTL 덮어쓰기 지원
            call_ttl_raw = kwargs.pop(ttl_kwarg, None)
            call_ttl = _seconds_from_ttl(call_ttl_raw)
            base_ttl = decorator_base_ttl if call_ttl is None else call_ttl
            final_ttl = _apply_jitter(base_ttl, jitter)

            redis_cli = get_redis_client()  # decode_responses=True 권장

            # ── 키 생성 ───────────────────────────────────
            if key_factory:
                cache_key = key_factory(args, kwargs, cache_prefix)
            else:
                # 위치/키워드 인자를 모두 포함해 안전하게 키 생성
                cache_key = _safe_cache_key(cache_prefix, args, kwargs)

            # ── 1) 캐시 조회 ───────────────────────────────
            if not refresh:
                try:
                    raw = redis_cli.get(cache_key)
                    if raw is not None:
                        mylogger.info(f"[redis] HIT  {cache_key}")
                        raw_str = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
                        return json.loads(raw_str)
                except Exception as e:
                    mylogger.warning(f"[redis] GET 실패: {e}")

            # ── 2) cache_only 처리 ────────────────────────
            if cache_only and not refresh:
                mylogger.info(f"[redis] MISS {cache_key} → 기본값 반환")
                return default_if_miss() if callable(default_if_miss) else default_if_miss

            # ── 3) 원본 함수 실행 ─────────────────────────
            mylogger.info(f"[redis] RUN  {cache_key} (refresh={refresh})")
            result = func(*args, **kwargs)

            # ── 4) 캐시 갱신 ─────────────────────────────
            try:
                # ttl<=0 이면 캐싱 생략
                if final_ttl is not None and final_ttl > 0:
                    payload = json.dumps(
                        to_jsonable_python(result),
                        default=_json_default,
                        ensure_ascii=False,
                    )
                    redis_cli.setex(cache_key, final_ttl, payload)
                    mylogger.info(f"[redis] SETEX {cache_key} ({final_ttl}s)")
                else:
                    mylogger.info(f"[redis] SKIP SETEX {cache_key} (ttl={final_ttl})")
            except Exception as e:
                mylogger.warning(f"[redis] SETEX 실패: {e}")

            return result

        return wrapper
    return decorator


def redis_async_cached(
    *,
    prefix: str | None = None,
    default_if_miss: Any = None,
    ttl: int | timedelta | None = None,                   # ⬅️ 데코레이터 인자: 기본 TTL(초 또는 timedelta)
    jitter: int | tuple[int, int] | None = 300,           # ⬅️ 스탬피드 완화용 지터(초). 0/None이면 미적용
    ttl_kwarg: str = "cache_ttl",                         # ⬅️ 호출 시점 TTL 덮어쓰기 키워드 인자 이름
    key_factory: Callable[[tuple, dict, str], str] | None = None,  # ⬅️ 캐시 키 커스터마이저(선택)
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]:
    """
    비동기 함수(async def) 결과를 Redis에 캐싱하는 데코레이터.

    Parameters
    ----------
    prefix : str | None
        Redis 키 prefix. 생략하면 함수 이름을 사용.
    default_if_miss : Any
        `cache_only=True`이고 캐시가 없을 때 반환할 기본값.
    ttl : int | timedelta | None
        기본 TTL(초). None이면 환경변수 REDIS_EXPIRE_TIME_H(시간)로부터 계산.
        0 또는 음수면 저장을 생략(캐시하지 않음).
    jitter : int | (int,int) | None
        TTL에 추가로 더할 난수(초). int면 [0, jitter], tuple이면 [lo, hi].
        0/None이면 지터 미적용.
    ttl_kwarg : str
        호출 시점에서 `await fn(..., cache_ttl=5)`처럼 TTL을 덮어쓸 때 사용할 키워드 인자명.
    key_factory : Callable[(args, kwargs, cache_prefix) -> str]
        캐시 키 생성 로직을 커스터마이즈하고 싶을 때 사용.
        기본값(None)일 경우 `_safe_cache_key(cache_prefix, args, kwargs)` 사용.

    호출 시 지원되는 특수 kwargs
    --------------------------
    refresh : bool = False
        True면 캐시를 무시하고 원본 함수를 실행한 뒤 갱신.
    cache_only : bool = False
        True이고 MISS면 원본 함수를 실행하지 않고 default_if_miss 반환.
    {ttl_kwarg} : int | timedelta | None
        이 호출에 한해 TTL 덮어쓰기.

    동작
    ----
    - 캐시 HIT : json.loads로 역직렬화해 반환(파이썬 기본 타입).
    - 캐시 MISS : 원본 실행 후 JSON 저장. (직렬화 불가 타입은 to_jsonable_python + _json_default로 처리)
    """
    # 환경 변수(시간) → 초
    env_hours = int(os.getenv("REDIS_EXPIRE_TIME_H", 12))
    env_default_ttl = env_hours * 60 * 60

    # 데코레이터 레벨 기본 TTL을 초 단위로 정규화
    decorator_base_ttl = _seconds_from_ttl(ttl)
    if decorator_base_ttl is None:
        decorator_base_ttl = env_default_ttl

    def decorator(func: Callable[..., Awaitable[Any]]):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("redis_async_cached 는 async 함수에만 사용할 수 있습니다.")

        cache_prefix = prefix or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            refresh: bool = kwargs.pop("refresh", False)
            cache_only: bool = kwargs.pop("cache_only", False)

            # 호출 시점 TTL 덮어쓰기 지원
            call_ttl_raw = kwargs.pop(ttl_kwarg, None)
            call_ttl = _seconds_from_ttl(call_ttl_raw)
            base_ttl = decorator_base_ttl if call_ttl is None else call_ttl
            final_ttl = _apply_jitter(base_ttl, jitter)

            redis_cli = get_redis_client_async()  # decode_responses=True 권장

            # ── 키 생성 ───────────────────────────────────
            if key_factory:
                cache_key = key_factory(args, kwargs, cache_prefix)
            else:
                # 위치/키워드 인자를 모두 포함해 안전하게 키 생성
                cache_key = _safe_cache_key(cache_prefix, args, kwargs)

            # ── 1) 캐시 조회 ───────────────────────────────
            if not refresh:
                try:
                    raw = await redis_cli.get(cache_key)
                    if raw is not None:
                        mylogger.info(f"[redis] HIT  {cache_key}")
                        raw_str = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
                        return json.loads(raw_str)
                except Exception as e:
                    mylogger.warning(f"[redis] GET 실패: {e}")

            # ── 2) cache_only 처리 ────────────────────────
            if cache_only and not refresh:
                mylogger.info(f"[redis] MISS {cache_key} → 기본값 반환")
                return default_if_miss

            # ── 3) 원본 함수 실행 ─────────────────────────
            mylogger.info(f"[redis] RUN  {cache_key} (refresh={refresh})")
            result = await func(*args, **kwargs)

            # ── 4) 캐시 갱신 ─────────────────────────────
            try:
                # ttl<=0 이면 캐싱 생략
                if final_ttl is not None and final_ttl > 0:
                    payload = json.dumps(
                        to_jsonable_python(result),
                        default=_json_default,
                        ensure_ascii=False,
                    )
                    await redis_cli.setex(cache_key, final_ttl, payload)
                    mylogger.info(f"[redis] SETEX {cache_key} ({final_ttl}s)")
                else:
                    mylogger.info(f"[redis] SKIP SETEX {cache_key} (ttl={final_ttl})")
            except Exception as e:
                mylogger.warning(f"[redis] SETEX 실패: {e}")

            return result

        return wrapper

    return decorator


M = TypeVar("M", bound=BaseModel)


def redis_async_cached_model(
    model: type[M],
    *,
    prefix: str | None = None,
    default_if_miss: Any = None,
    ttl: int | timedelta | None = None,                # ⬅️ 데코레이터 인자: 기본 TTL
    jitter: int | tuple[int, int] | None = 300,        # ⬅️ 스탬피드 방지용 지터(초). 0/None이면 미적용
    ttl_kwarg: str = "cache_ttl",                      # ⬅️ 호출 시점 덮어쓰기 키워드 인자 이름
):
    """
    Pydantic 모델(M) 또는 모델 리스트(list[M])을 반환하는 비동기 함수용 Redis 캐시 데코레이터.

    Parameters
    ----------
    model : type[M]
        캐시 복원에 사용할 Pydantic 모델 클래스.
    prefix : str | None
        Redis 키 prefix. 생략하면 함수 이름 사용.
    default_if_miss : Any
        `cache_only=True` 이고 캐시 미스일 때 반환할 기본값.
    ttl : int | timedelta | None
        기본 TTL(초). 생략(None) 시 환경변수 REDIS_EXPIRE_TIME_H(시간)으로부터 계산.
        0 또는 음수면 저장을 생략(캐시하지 않음).
    jitter : int | tuple[int,int] | None
        TTL에 더해줄 지터 범위(초). int면 [0, jitter], tuple이면 [lo, hi].
        0/None 이면 지터 미적용.
    ttl_kwarg : str
        함수 호출 시 `await fn(..., cache_ttl=5)` 처럼 TTL을 덮어쓸 때 사용할 키워드 인자 이름.

    동작
    ----
    - 캐시 HIT : 저장 당시 구조(단일/리스트)로 복원.
    - 캐시 MISS : 원본 실행 후 JSON 저장.
    - refresh=True : 캐시 무시, 원본 실행 후 갱신.
    - cache_only=True & MISS : default_if_miss 반환.
    - 호출 시점 TTL 덮어쓰기 : `await fn(..., cache_ttl=10)`
    """
    # 환경변수(시간) → 초
    env_hours = int(os.getenv("REDIS_EXPIRE_TIME_H", 12))
    env_default_ttl = env_hours * 60 * 60

    # 데코레이터 인자의 기본 TTL을 미리 초 단위로 정규화(호출 시 계산 오버헤드↓)
    decorator_base_ttl = _seconds_from_ttl(ttl)
    if decorator_base_ttl is None:
        decorator_base_ttl = env_default_ttl

    def decorator(func: Callable[..., Awaitable[M] | Awaitable[list[M]]]):
        if not inspect.iscoroutinefunction(func):
            raise TypeError("redis_async_cached_model 데코레이터는 async 함수에만 사용 가능합니다.")

        cache_prefix = prefix or func.__name__

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            refresh: bool = kwargs.pop("refresh", False)
            cache_only: bool = kwargs.pop("cache_only", False)

            # 호출 시점 TTL 덮어쓰기 지원
            call_ttl_raw = kwargs.pop(ttl_kwarg, None)
            call_ttl = _seconds_from_ttl(call_ttl_raw)
            base_ttl = decorator_base_ttl if call_ttl is None else call_ttl

            # 최종 TTL 계산(+지터)
            final_ttl = _apply_jitter(base_ttl, jitter)

            redis_cli = get_redis_client_async()  # decode_responses=True 권장

            # ── 키 생성 ────────────────────────────────────
            cache_key = _safe_cache_key(cache_prefix, args, kwargs)

            # ── 1) 캐시 조회 ───────────────────────────────
            if not refresh:
                try:
                    raw = await redis_cli.get(cache_key)
                    if raw is not None:
                        mylogger.info(f"[redis] HIT  {cache_key}")
                        raw_str = raw.decode("utf-8") if isinstance(raw, (bytes, bytearray)) else raw
                        # 단일 모델 시도
                        try:
                            return model.model_validate_json(raw_str)  # type: ignore[return-value]
                        except Exception:
                            # 리스트 시도
                            data = json.loads(raw_str)
                            if isinstance(data, list):
                                return [model.model_validate(d) for d in data]  # type: ignore[return-value]
                            return data
                except Exception as e:
                    mylogger.warning(f"[redis] GET 실패: {e}")

            # ── 2) cache_only 처리 ─────────────────────────
            if cache_only and not refresh:
                mylogger.info(f"[redis] MISS {cache_key} → 기본값 반환")
                return default_if_miss

            # ── 3) 원본 실행 ───────────────────────────────
            result = await func(*args, **kwargs)

            # ── 4) 캐시 갱신 ───────────────────────────────
            try:
                # ttl<=0 이면 캐시 저장 생략(요구사항에 맞게 정책 선택)
                if final_ttl is not None and final_ttl > 0:
                    if isinstance(result, list):
                        if result and isinstance(result[0], BaseModel):
                            payload = json.dumps([m.model_dump(mode="json") for m in result], ensure_ascii=False)
                        else:
                            payload = json.dumps(to_jsonable_python(result), default=_json_default, ensure_ascii=False)
                    elif isinstance(result, BaseModel):
                        payload = result.model_dump_json()
                    else:
                        payload = json.dumps(to_jsonable_python(result), default=_json_default, ensure_ascii=False)

                    await redis_cli.setex(cache_key, final_ttl, payload)
                    mylogger.info(f"[redis] SETEX {cache_key} ({final_ttl}s)")
                else:
                    mylogger.info(f"[redis] SKIP SETEX {cache_key} (ttl={final_ttl})")
            except Exception as e:
                mylogger.warning(f"[redis] SETEX 실패: {e}")

            return result

        return wrapper
    return decorator