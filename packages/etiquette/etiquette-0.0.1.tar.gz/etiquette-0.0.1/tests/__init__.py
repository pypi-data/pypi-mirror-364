#!/usr/bin/env python3.9
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/src/etiquette/__init__.py
# VERSION:     0.0.1
# CREATED:     2025-07-19 13:57
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION: https://www.w3docs.com/snippets/python/what-is-init-py-for.html
#
# HISTORY:
# *************************************************************
"""
Tests for Etiquette plugin for ASGI frameworks
"""

### Standard packages ###
from asyncio import Lock, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Annotated, AsyncGenerator, Final

### Third-party packages ###
from fastapi import FastAPI
from fastapi.param_functions import Depends
from fastapi.testclient import TestClient
from pytest import fixture
from starlette.requests import Request
from starlette.responses import JSONResponse

### Local modules ###
from etiquette import Decorum, Etiquette


@fixture
def test_client() -> TestClient:
  """
  Sets up a FastAPI TestClient wrapped around an application implementing both
  SafeCounter and UnsafeCounter increment call by Decorum

  ---
  :return: test client fixture used for local testing
  :rtype: fastapi.testclient.TestClient
  """

  @asynccontextmanager
  async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    Etiquette.initiate(max_concurrent_tasks=8)
    yield
    await Etiquette.release()

  app = FastAPI(lifespan=lifespan)

  @dataclass
  class UnsafeCounter:
    """Counter without thread safety - demonstrates race condition"""

    count: int = 0

    @property
    async def current(self) -> int:
      return self.count

    async def increment(self) -> None:
      await sleep(0.001)
      self.count += 1

  @dataclass
  class SafeCounter:
    """Counter with thread safety - fixes race condition"""

    count: int = 0
    _lock: Lock = field(default_factory=Lock, init=False)

    @property
    async def current(self) -> int:
      async with self._lock:
        return self.count

    async def increment(self) -> None:
      async with self._lock:
        current = self.count
        await sleep(0.001)
        self.count = current + 1

  safe_counter: SafeCounter = SafeCounter()

  @app.get("/safe-counter")
  async def increment_safe_counter(decorum: Annotated[Decorum, Depends(Decorum)]) -> int:
    await decorum.add_task(safe_counter.increment)
    return await safe_counter.current

  unsafe_counter: UnsafeCounter = UnsafeCounter()

  @app.get("/unsafe-counter")
  async def increment_unsafe_counter(decorum: Annotated[Decorum, Depends(Decorum)]) -> int:
    await decorum.add_task(unsafe_counter.increment)
    return await unsafe_counter.current

  @app.exception_handler(ValueError)
  def csrf_protect_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=520, content={"detail": str(exc)})

  return TestClient(app)


__all__: Final[tuple[str, ...]] = ("test_client",)
