#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/examples/litestar_app.py
# VERSION:     0.0.1
# CREATED:     2025-07-23 14:20
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from asyncio import sleep
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Final

### Third-party packages ###
from litestar import Litestar
from litestar.di import Provide
from litestar.handlers.http_handlers.decorators import get

### Local modules ###
from etiquette import Decorum, Etiquette


@asynccontextmanager
async def lifespan(_: Litestar) -> AsyncGenerator[None, None]:
  Etiquette.initiate(max_concurrent_tasks=16)
  yield
  await Etiquette.release()


@get("/add-task")
async def add_new_task(decorum: Decorum) -> str:
  async def sleep_3() -> None:
    await sleep(3)
    print("task done")

  await decorum.add_task(sleep_3)
  return "OK"


app: Litestar = Litestar(
  dependencies={"decorum": Provide(Decorum, sync_to_thread=True)},
  lifespan=[lifespan],
  route_handlers=[add_new_task],
)

__all__: Final[tuple[str, ...]] = ("app",)
