import asyncio
import signal
from typing import List
from dotenv import load_dotenv
import pebble
import uvloop

from zenx.logger import configure_logger
from zenx.pipelines.manager import PipelineManager
from zenx.clients.database import DBClient
from zenx.clients.http import HttpClient
from zenx.spiders import Spider
from zenx.settings import settings
load_dotenv()


class Engine:
    

    def __init__(self, forever: bool) -> None:
        self.forever = forever
        self.shutdown_event = asyncio.Event()
    

    def _shutdown_handler(self) -> None:
        self.shutdown_event.set()


    async def _execute(self, spider_name: str) -> None:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, self._shutdown_handler)
        loop.add_signal_handler(signal.SIGTERM, self._shutdown_handler)

        spider_cls = Spider.get_spider(spider_name)
        logger = configure_logger(spider_cls.name)
        client = HttpClient.get_client(spider_cls.client_name)(logger=logger, settings=settings) # type: ignore[call-arg]
        
        db = DBClient.get_db(settings.DB_TYPE)(logger=logger, settings=settings)
        await db.start()

        pm = PipelineManager(
            pipeline_names=spider_cls.pipelines, 
            logger=logger, 
            db=db, 
            settings=settings
        )
        await pm.start_pipelines()

        spider = spider_cls(client=client, pm=pm, logger=logger, settings=settings)
        try:
            if self.forever:
                while not self.shutdown_event.is_set():
                    try:
                        await spider.crawl()
                    except Exception:
                        logger.exception("crawl")
                        await asyncio.sleep(0.01)
            else:
                await spider.crawl()
        finally:
            if self.shutdown_event.is_set():
                logger.info("shutdown", spider=spider_name)
            if spider.background_tasks:
                logger.debug("waiting", background_tasks=len(spider.background_tasks), belong_to="spider")
                await asyncio.gather(*spider.background_tasks)
            await client.close()
            await db.close()
            await pm.close_pipelines()
    

    def run_spider(self, spider: str) -> None:
        uvloop.run(self._execute(spider))


    def run_spiders(self, spiders: List[str]) -> None:
        with pebble.ProcessPool() as pool:
            for spider in spiders:
                pool.schedule(self.run_spider, [spider])
