from datetime import datetime, timedelta
import time
from mjkit.cache.time_cache import TimedCache
import logging
from typing import Callable

class MidnightTimedCache(TimedCache):
    """
    > <중요!> 해당 Cache가 적용되면 멀티스레딩이 적용되지 않음.

    자정(00:00)을 기준으로 TTL(Time-To-Live)을 자동 설정하는 TimedCache 확장 클래스.

    이 클래스는 캐시 지속 시간(TTL)을 "오늘 자정까지 남은 시간"으로 자동 설정하여,
    매일 자정 이후에는 기존 캐시를 무효화하고 새로 계산된 값을 사용하도록 합니다.

    주요 특징
    ----------
    - 매일 자정 기준으로 캐시 만료 처리
    - API 호출 또는 일일 단위 계산 결과 캐싱에 적합
    - TimedCache와 동일한 방식으로 작동하지만 TTL이 자동 갱신되지 않음

    Attributes
    ----------
    ttl : int
        자정까지 남은 초 (초 단위 TTL)
    cache : dict
        캐시 저장소: key=(args, kwargs), value=(result, timestamp)
    lock : threading.Lock
        멀티스레드 환경에서의 동기화를 위한 락
    logger : logging.Logger
        로깅을 위한 로거 객체

    Example
    -------
    >>> @MidnightTimedCache()
    >>> def get_stock_summary():
    >>>     print("📦 실제 API 호출 발생!")
    >>>     return {"timestamp": time.time()}
    >>>
    >>>
    >>> print("1회 호출 결과:", get_stock_summary())  # 실제 호출
    >>> time.sleep(2)
    >>> print("2회 호출 결과:", get_stock_summary())  # 캐시된 결과 사용
    >>> time.sleep(2)
    >>> print("3회 호출 결과:", get_stock_summary())  # 여전히 캐시 사용됨
    >>>
    >>> # 자정까지 캐시되는 데코레이터 인스턴스 생성
    >>> cache_until_midnight = MidnightTimedCache(log_level=logging.INFO)
    >>>
    >>> @cache_until_midnight
    >>> def get_stock_summary():
    >>>     print("📦 실제 API 호출 발생!")
    >>>     return {"timestamp": time.time()}
    >>>
    >>> print("1회 호출 결과:", get_stock_summary())  # 실제 호출
    >>> time.sleep(2)
    >>> print("2회 호출 결과:", get_stock_summary())  # 캐시된 결과 사용
    >>> time.sleep(2)
    >>> print("3회 호출 결과:", get_stock_summary())  # 여전히 캐시 사용됨
    >>> fetch_market_summary()
    📈 API 호출 발생
    >>> fetch_market_summary()
    # 캐시 HIT, API 호출 없음
    """

    def __init__(self, log_level: int = logging.INFO):
        """
        MidnightTimedCache 생성자. 자정까지 남은 시간을 TTL로 설정합니다.

        Parameters
        ----------
        log_level : int, optional
            로깅 레벨 설정 (기본값: logging.INFO)
        """
        ttl_seconds = self._seconds_until_midnight()
        super().__init__(ttl_seconds=ttl_seconds, log_level=log_level)

    def _seconds_until_midnight(self) -> int:
        """
        현재 시점으로부터 다음 자정까지 남은 시간을 초 단위로 계산합니다.

        Returns
        -------
        int
            자정까지 남은 초
        """
        now = datetime.now()
        next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return int((next_midnight - now).total_seconds())

    def __call__(self, func: Callable):
        """
        데코레이터로 함수에 적용되어 자정까지 TTL 기반 캐시를 설정합니다.

        Notes
        -----
        TimedCache의 __call__을 그대로 사용하지만, TTL은 자정까지로 고정되며
        각 호출 시 TTL이 갱신되지는 않습니다.

        Parameters
        ----------
        func : Callable
            캐시를 적용할 대상 함수

        Returns
        -------
        Callable
            자정 기준 TTL이 적용된 캐시 래핑 함수
        """
        return super().__call__(func)

# ✅ 실행 예시
if __name__ == "__main__":
    import time
    @MidnightTimedCache()
    def get_stock_summary():
        print("📦 실제 API 호출 발생!")
        return {"timestamp": time.time()}


    print("1회 호출 결과:", get_stock_summary())  # 실제 호출
    time.sleep(2)
    print("2회 호출 결과:", get_stock_summary())  # 캐시된 결과 사용
    time.sleep(2)
    print("3회 호출 결과:", get_stock_summary())  # 여전히 캐시 사용됨

    # 자정까지 캐시되는 데코레이터 인스턴스 생성
    cache_until_midnight = MidnightTimedCache(log_level=logging.INFO)

    @cache_until_midnight
    def get_stock_summary():
        print("📦 실제 API 호출 발생!")
        return {"timestamp": time.time()}

    print("1회 호출 결과:", get_stock_summary())  # 실제 호출
    time.sleep(2)
    print("2회 호출 결과:", get_stock_summary())  # 캐시된 결과 사용
    time.sleep(2)
    print("3회 호출 결과:", get_stock_summary())  # 여전히 캐시 사용됨

    # 결과는 오늘 자정까지 유지되며, 이후 첫 호출 시 새로 계산됨
