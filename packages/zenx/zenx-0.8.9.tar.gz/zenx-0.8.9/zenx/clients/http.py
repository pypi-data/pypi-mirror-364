from __future__ import annotations
import parsel
import random
from curl_cffi.requests.impersonate import BrowserTypeLiteral
from curl_cffi import AsyncSession, Response as CurlResponse
from abc import ABC, abstractmethod
import asyncio
from dataclasses import dataclass
from typing import Any, ClassVar, Tuple, Type, Dict, get_args
import json
from structlog import BoundLogger

from zenx.settings import Settings
from zenx.utils import get_time


@dataclass
class Response:
    url: str
    status: int
    text: str
    headers: Dict
    responded_at: int
    requested_at: int
    latency_ms: int

    def json(self) -> Any:
        return json.loads(self.text)
    
    def selector(self) -> parsel.Selector:
        sel = parsel.Selector(self.text)
        return sel


class HttpClient(ABC):
    # central registry
    name: ClassVar[str]
    _registry: ClassVar[Dict[str, Type[HttpClient]]] = {}
    

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "name"):
            raise TypeError(f"HttpClient subclass {cls.__name__} must have a 'name' attribute.")
        cls._registry[cls.name] = cls


    @classmethod
    def get_client(cls, name: str) -> Type[HttpClient]:
        if name not in cls._registry:
            raise ValueError(f"HttpClient '{name}' is not registered. Available http clients: {list(cls._registry.keys())}")
        return cls._registry[name]
    

    def __init__(self, logger: BoundLogger, settings: Settings) -> None:
        self.logger = logger
        self.settings = settings
        self._session_pool: asyncio.Queue
    
    
    @abstractmethod
    async def request(
        self,
        url: str,
        method: str = "GET",
        headers: Dict | None = None,
        proxy: str | None = None,
        use_sessions: bool = False,
        **kwargs,
    ) -> Response:
        ...
    

    @abstractmethod
    async def close(self) -> None:
        ...



class CurlCffi(HttpClient):
    name = "curl_cffi"


    def __init__(self, logger: BoundLogger, settings: Settings) -> None:
        super().__init__(logger, settings)
        self._fingerprints: Tuple[str] = get_args(BrowserTypeLiteral)
        self._session_pool = asyncio.Queue(maxsize=settings.SESSION_POOL_SIZE)
        for _ in range(settings.SESSION_POOL_SIZE):
            impersonate = self._get_random_fingerprint()
            self._session_pool.put_nowait(AsyncSession(max_clients=1, impersonate=impersonate))
        self.logger.debug("created", sessions=self._session_pool.qsize(), client=self.name)

        
    def _get_random_fingerprint(self) -> str:
        chosen_fingerprint = random.choice(self._fingerprints) 
        return chosen_fingerprint

    
    async def request(
        self,
        url: str,
        method: str = "GET",
        headers: Dict | None = None,
        proxy: str | None = None,
        use_sessions: bool = False,
        *,
        impersonate: str | None = None,
        **kwargs,
    ) -> Response:
        if impersonate is None:
            impersonate = self._get_random_fingerprint()
        if not use_sessions:
            async with AsyncSession() as session:
                try:
                    req_at = get_time()
                    response: CurlResponse = await session.request(
                        url=url, 
                        method=method, 
                        headers=headers, 
                        proxy=proxy,
                        verify=False,
                        impersonate=impersonate,
                        **kwargs,
                    )
                    recv_at = get_time()
                    latency = recv_at - req_at
                    self.logger.debug("response", status=response.status_code, url=url, impersonate=impersonate, client=self.name, requested_at=req_at, responded_at=recv_at, latency_ms=latency)
                except Exception:
                    self.logger.exception("request", url=url, client=self.name)
                    raise
        else:
            # each session has its own fingerprint set
            kwargs.pop("impersonate", None)
            session: AsyncSession = await self._session_pool.get()
            try:
                req_at = get_time()
                response: CurlResponse = await session.request(
                    url=url, 
                    method=method, 
                    headers=headers, 
                    proxy=proxy,
                    verify=False,
                    **kwargs,
                )
                recv_at = get_time()
                latency = recv_at - req_at
                self.logger.debug("response", status=response.status_code, url=url, impersonate=session.impersonate, client=self.name, requested_at=req_at, responded_at=recv_at, latency_ms=latency)
            except Exception:
                self.logger.exception("request", url=url, client=self.name)
                raise
            finally:
                self._session_pool.put_nowait(session)

        return Response(
            url=response.url,
            status=response.status_code,
            text=response.text,
            headers=dict(response.headers),
            requested_at=req_at,
            responded_at=recv_at,
            latency_ms=latency,
        )
    
    
    async def close(self) -> None:
        count = self._session_pool.qsize()
        async with asyncio.TaskGroup() as tg:
            while not self._session_pool.empty():
                session: AsyncSession = await self._session_pool.get()
                tg.create_task(session.close())
        self.logger.debug("closed", sessions=count, client=self.name)
