from structlog import BoundLogger
from typing import Dict
import httpx
from datetime import datetime, timezone

from zenx.settings import Settings
from zenx.monitors.base import Monitor


try:
    import psutil


    class ItxpMonitor(Monitor):
        name = "itxp"
        required_settings = ["MONITOR_ITXP_TOKEN"]


        def __init__(self, logger: BoundLogger, settings: Settings) -> None:
            super().__init__(logger, settings)
            self.token = self.settings.MONITOR_ITXP_TOKEN
            self.uri = self.settings.MONITOR_ITXP_URI


        @staticmethod
        def _get_system_info() -> Dict:
            return {
                "cpu_percent_per_core": psutil.cpu_percent(interval=1, percpu=True),
                "disk_percent": psutil.disk_usage('/').percent,
                "ram_percent": psutil.virtual_memory().percent,
                "swap_percent": psutil.swap_memory().percent
            }


        async def open(self) -> None:
            pass 


        async def process_stats(self, stats: Dict, producer: str) -> None:
            system_info = self._get_system_info()
            payload = {
                "hostname": "",
                "timestamp": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                "apps": {},
            }


        async def close(self) -> None:
            pass

except ModuleNotFoundError:
    # proxy pattern
    class ItxpMonitor(Monitor):
        name = "itxp"
        required_settings = []

        _ERROR_MESSAGE = (
            f"The '{name}' pipeline is disabled because the required dependencies are not installed. "
            "Please install it to enable this feature:\n\n"
            "  pip install 'zenx[itxp]'"
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise ImportError(self._ERROR_MESSAGE)
        
        async def open(self) -> None: pass
        async def process_stats(self, stats: Dict, producer: str) -> None: pass
        async def close(self) -> None: pass
