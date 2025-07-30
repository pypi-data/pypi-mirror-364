#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/examples/fastapi_app.py
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


@app.get("/add-task")
async def add_new_task(decorum: Annotated[Decorum, Depends(Decorum)]) -> str:
  async def sleep_3() -> None:
    await sleep(3)
    print("task done")

  await decorum.add_task(sleep_3)
  return "OK"


__all__: Final[tuple[str, ...]] = ("app",)
