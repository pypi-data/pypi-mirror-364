from __future__ import annotations

import hashlib

import numpy as np
from typing import Literal, Any, Callable, Awaitable
import datetime
import time
import matplotlib.pyplot as plt
import yfinance as yf
import pandas as pd
import json, os, redis, functools, inspect

from darts import TimeSeries
from ..common.connection import get_redis_client, get_redis_client_async


from utils_hj3415 import setup_logger

mylogger = setup_logger(__name__,'INFO')


def get_raw_data(ticker: str, max_retries: int = 3, delay_sec: int = 2) -> pd.DataFrame:
    """
    Yahoo Finance에서 특정 티커의 최근 4년간 주가 데이터를 가져옵니다.

    Args:
        ticker (str): 조회할 종목의 티커 (예: "005930.KQ").
        max_retries (int, optional): 최대 재시도 횟수. 기본값은 3.
        delay_sec (int, optional): 재시도 전 대기 시간 (초). 기본값은 2초.

    Returns:
        pd.DataFrame: 주가 데이터프레임. 실패 시 빈 DataFrame 반환.
    """
    today = datetime.datetime.today()
    four_years_ago = today - datetime.timedelta(days=365 * 4)

    for attempt in range(1, max_retries + 1):
        try:
            data = yf.download(
                tickers=ticker,
                start=four_years_ago.strftime('%Y-%m-%d'),
                # end=today.strftime('%Y-%m-%d')  # 생략 시 최신 날짜까지 자동 포함
            )

            if not data.empty:
                return data
            else:
                print(f"[{attempt}/{max_retries}] '{ticker}' 데이터가 비어 있습니다. {delay_sec}초 후 재시도합니다...")

        except Exception as e:
            print(f"[{attempt}/{max_retries}] '{ticker}' 다운로드 중 오류 발생: {e}. {delay_sec}초 후 재시도합니다...")

        time.sleep(delay_sec)

    mylogger.error(f"'{ticker}' 주가 데이터를 최대 {max_retries}회 시도했지만 실패했습니다.")
    return pd.DataFrame()


def timeseries_to_dataframe(forecast: TimeSeries) -> pd.DataFrame:
    forecast_df = forecast.to_dataframe()
    mylogger.debug(forecast_df)
    return forecast_df


def show_graph(data: dict[str, list]) -> None:
    """
    JSON 직렬화가 가능한 dict( keys = ds, actual, forecast, lower, upper )를
    받아 matplotlib 그래프를 표시한다.

    Parameters
    ----------
    data   : dict
        {"ds": [...], "actual": [...], "forecast": [...], "lower": [...], "upper": [...]}
        * ds        : 날짜 문자열(YYYY-MM-DD)
        * actual    : 실제값. None → 결측
        * forecast  : 예측값(포인트). None → 결측
        * lower/upper : (선택) 예측구간 하한/상한. None → 결측
    """
    # ──────────────────────────────────────
    # ① dict → DataFrame
    # ──────────────────────────────────────
    df = pd.DataFrame(data)
    df["ds"] = pd.to_datetime(df["ds"])
    df.set_index("ds", inplace=True)

    # 숫자형 변환 (None → NaN)
    for col in ["actual", "forecast", "lower", "upper"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # ──────────────────────────────────────
    # ② plot
    # ──────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 6))

    df["actual"].plot(ax=ax, label="Actual", lw=1.6)
    df["forecast"].plot(ax=ax, label="Forecast", lw=1.6, color="tab:orange")

    # 불확실성 구간이 있으면 음영으로 표시
    if {"lower", "upper"}.issubset(df.columns):
        ax.fill_between(
            df.index,
            df["lower"],
            df["upper"],
            color="tab:orange",
            alpha=0.5,
            label="90% interval",
        )

    ax.set_title("nbeats forecast")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()


def _make_key(tickers: list[str], trend: str) -> str:
    norm = sorted(set(t.lower() for t in tickers))       # 정렬·중복 제거
    sha1 = hashlib.sha1(",".join(norm).encode()).hexdigest()[:16]
    return f"{trend}:{sha1}"                             # 짧고 충돌 낮음


def redis_cached(prefix: str | None = None, default_if_miss=None):
    """Redis 캐싱 데코레이터

    Args:
        prefix     : Redis 키 prefix (기본 = 함수.__name__)
        default_if_miss : 캐시가 없을 때 함수 실행 대신 반환할 기본값 (기본: None)
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


def judge_trend(fcst: np.ndarray, slope_th: float = 0.001, pct_th  : float = 2.0) -> Literal["상승", "하락", "횡보", "미정"]:
    fcst = fcst[~np.isnan(fcst)]
    if len(fcst) < 15:          # 데이터가 너무 짧으면
        return "미정"

    x = np.arange(len(fcst))
    slope = np.polyfit(x, fcst, 1)[0] / fcst.mean()   # 상대 기울기(%)
    delta_pct = (fcst[-1] - fcst[0]) / fcst[0] * 100

    if slope >  slope_th and delta_pct >  pct_th:   return "상승"
    if slope < -slope_th and delta_pct < -pct_th:   return "하락"
    return "횡보"









