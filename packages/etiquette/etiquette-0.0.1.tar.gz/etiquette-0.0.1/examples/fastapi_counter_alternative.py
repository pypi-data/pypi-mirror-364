#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/examples/fastapi_counter_alternative.py
# VERSION:     0.0.1
# CREATED:     2025-07-24 11:22
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION: Alternative implementation using asyncio.AtomicCounter
#
# HISTORY:
# *************************************************************

### Standard packages ###
from asyncio import AtomicCounter, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated, AsyncGenerator, Final

### Third-party packages ###
from fastapi import FastAPI
from fastapi.param_functions import Depends

### Local modules ###
from etiquette import Decorum, Etiquette


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
  Etiquette.initiate(max_concurrent_tasks=16)
  yield
  await Etiquette.release()


app: FastAPI = FastAPI(lifespan=lifespan)


@dataclass
class Counter:
  _counter: AtomicCounter = AtomicCounter()

  async def increment(self) -> None:
    current_count = self._counter.add(1)
    await sleep(delay=1)
    print(f"{current_count=}")


counter: Counter = Counter()


@app.get("/add-task")
async def add_new_task(decorum: Annotated[Decorum, Depends(Decorum)]) -> str:

  await decorum.add_task(counter.increment)
  return "OK"


__all__: Final[tuple[str, ...]] = ("app",)
