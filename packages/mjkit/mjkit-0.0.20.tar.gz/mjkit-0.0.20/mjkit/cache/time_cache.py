import threading
import time
from functools import wraps
from typing import Callable
from mjkit.mixin import LoggingMixin
import logging


class TimedCache(LoggingMixin):
    """
    > <중요!> 해당 Cache가 적용되면 멀티스레딩이 적용되지 않음.

    일정 시간 동안 함수 결과를 메모리에 캐싱하는 데코레이터 클래스.

    이 데코레이터는 주어진 TTL(Time-to-Live) 동안 같은 인자 조합으로 호출된 함수의 결과를
    캐시로부터 반환합니다. TTL이 만료되면 캐시를 무시하고 함수를 다시 호출합니다.

    주로 API 호출, 데이터베이스 쿼리, 느린 연산 결과를 일정 시간 재사용하고자 할 때 사용됩니다.

    Attributes
    ----------
    ttl : int
        캐시 유지 시간 (초 단위)
    cache : dict
        내부 캐시 딕셔너리: key=(args, kwargs), value=(result, timestamp)
    lock : threading.Lock
        멀티스레드 환경에서의 동기화를 위한 락 객체

    Parameters
    ----------
    ttl_seconds : int
        각 함수 결과가 유지될 캐시 지속 시간 (초)
    log_level : int, optional
        로깅 레벨 (기본값: logging.INFO)

    Example
    -------
    >>> @TimedCache(ttl_seconds=5)
    ... def slow_function(x):
    ...     print("실제 실행됨!")
    ...     return x ** 2
    ...
    >>> slow_function(2)
    실제 실행됨!
    4
    >>> slow_function(2)
    4  # 캐시에서 반환됨
    >>> time.sleep(6)
    >>> slow_function(2)
    실제 실행됨!
    4  # TTL 만료로 재실행
    """

    def __init__(self, ttl_seconds: int, log_level: int = logging.INFO):
        super().__init__(level=log_level)
        self.ttl = ttl_seconds
        self.cache = {}
        self.lock = threading.Lock()

    def _is_cache_expired(self, timestamp):
        from datetime import datetime, time as dt_time
        now = datetime.now()
        midnight = datetime.combine(now.date(), dt_time(0, 0))
        return timestamp < midnight.timestamp()

    def __call__(self, func: Callable):
        """
        데코레이터로서의 TimedCache 실행 메서드.

        내부적으로 인자(args, kwargs)를 기준으로 키를 만들고,
        해당 키에 대한 캐시가 존재하고 TTL이 유효하면 캐시된 값을 반환합니다.
        TTL이 만료되었거나 캐시가 없으면 실제 함수를 호출하고 그 결과를 저장합니다.

        Parameters
        ----------
        func : Callable
            캐시를 적용할 대상 함수

        Returns
        -------
        Callable
            TTL 기반 캐시가 적용된 래핑 함수

        Example
        -------
        >>> @TimedCache(ttl_seconds=10)
        ... def get_api_result(param):
        ...     print("API 호출 발생!")
        ...     return expensive_api_call(param)
        ...
        >>> get_api_result("AAPL")
        API 호출 발생!
        ...
        >>> get_api_result("AAPL")  # 10초 이내 재호출 → 캐시 사용
        ...
        """
        cache = self.cache
        lock = self.lock
        logger = self.logger

        @wraps(func)
        def wrapped(*args, **kwargs):
            now = time.time()
            key = (args, tuple(sorted(kwargs.items())))

            with lock:
                if key in cache:
                    result, timestamp = cache[key]
                    if not self._is_cache_expired(timestamp):
                        logger.info(f"✅ 캐시 HIT - key={key}")
                        return result
                    else:
                        logger.info(f"⏰ 캐시 만료 - key={key}")
                else:
                    logger.info(f"📥 캐시 MISS - key={key}")

                result = func(*args, **kwargs)
                cache[key] = (result, now)
                logger.info(f"💾 캐시 저장 완료 - key={key}")
                return result

        return wrapped


if __name__ == "__main__":
    # 위에서 정의한 TimedCache 사용
    cache_5s = TimedCache(ttl_seconds=5)


    @cache_5s
    def get_current_time():
        print("⏱️ 실제 함수 호출됨!")
        return time.time()


    print("1회 호출:", get_current_time())  # 호출됨
    time.sleep(2)
    print("2회 호출:", get_current_time())  # 캐시 사용됨 (5초 내)
    time.sleep(4)
    print("3회 호출:", get_current_time())  # 캐시 만료됨 → 다시 호출
    print()


    @cache_5s
    def multiply(x, y=1):
        print("📦 실제 함수 실행")
        return x * y


    print(multiply(3, y=4))  # 캐시 MISS
    print(multiply(3, y=4))  # 캐시 HIT
    print(multiply(4, y=4))  # 또 다른 키 → 캐시 MISS
    print("현재 캐시 상태:", cache_5s.cache)
