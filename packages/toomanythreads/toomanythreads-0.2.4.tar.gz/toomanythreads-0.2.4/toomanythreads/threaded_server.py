import threading
from functools import cached_property

import uvicorn
from fastapi import FastAPI
from loguru import logger as log
from toomanyports import PortManager

from toomanythreads import ManagedThread


class ThreadedServer(FastAPI):
    def __init__(
            self,
            host: str = None,
            port: int = None,
            reload: bool = False,
            verbose: bool = True,
    ) -> None:
        self.host = "localhost" if host is None else host
        self.port = PortManager.random_port() if port is None else port
        PortManager.kill(self.port, force=True)
        self.verbose = verbose
        super().__init__(debug=self.verbose)
        if self.verbose:
            try: log.success(f"[{self}]: Initialized successfully!\n  - host={self.host}\n  - port={self.port}")
            except Exception: log.success(f"Initialized new ThreadedServer successfully!\n  - host={self.host}\n  - port={self.port}")

    @cached_property
    def url(self):
        return f"http://{self.host}:{self.port}"

    @cached_property
    def uvicorn_cfg(self) -> uvicorn.Config:
        return uvicorn.Config(
            app=self,
            host=self.host,
            port=self.port,
            # reload=True,
            # log_config=,
        )

    @cached_property
    def thread(self) -> threading.Thread:  # type: ignore
        def proc(self):
            if self.verbose: log.info(f"[{self}]: Launching microservice on {self.host}:{self.port}")
            server = uvicorn.Server(config=self.uvicorn_cfg)
            server.run()

        return ManagedThread(proc, self)
