import time
from typing import Dict
import functools


def get_time() -> int:
    """ current unix time in milliseconds """
    return int(time.time() * 1000)


def log_processing_time(func):
    @functools.wraps(func)
    async def wrapper(self, item: Dict, spider: str, *args, **kwargs) -> Dict:
        start_time = get_time()
        result = await func(self, item, spider, *args, **kwargs)
        end_time = get_time()
        processed_time = end_time - start_time    
        self.logger.info("processed", id=item['_id'], time_ms=processed_time, pipeline=self.name, started_at=start_time, finished_at=end_time)
        return result
    return wrapper

