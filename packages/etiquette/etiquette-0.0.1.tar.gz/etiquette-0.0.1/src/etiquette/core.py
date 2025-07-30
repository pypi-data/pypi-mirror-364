#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/src/etiquette/core.py
# VERSION:     0.0.1
# CREATED:     2025-07-23 14:20
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from __future__ import annotations
from asyncio import Queue, Semaphore, Task, create_task, gather, sleep, wait_for
from asyncio.exceptions import CancelledError, TimeoutError
from logging import Logger, getLogger
from typing import Any, ClassVar, Final

### Local modules ###
from etiquette._types import TaskData

logger: Logger = getLogger(__name__)


class Etiquette:
  active_tasks: ClassVar[set[Task[Any]]] = set()
  running: ClassVar[bool] = False
  semaphore: ClassVar[Semaphore]
  task_queue: ClassVar[Queue[TaskData]]
  worker_task: ClassVar[Task[None]]

  @classmethod
  def initiate(cls, max_concurrent_tasks: int = 2) -> None:
    """Start the background worker that processes queued tasks"""
    cls.active_tasks = set()
    cls.running = True
    cls.semaphore = Semaphore(value=max_concurrent_tasks)
    cls.task_queue = Queue()
    cls.worker_task = create_task(coro=cls._worker())

  @classmethod
  async def release(cls) -> None:
    if cls.running:
      cls.running = False
      if cls.worker_task:
        cls.worker_task.cancel()
        try:
          await cls.worker_task
        except CancelledError:
          pass
      if cls.active_tasks:
        await gather(*cls.active_tasks, return_exceptions=True)

  @classmethod
  async def _worker(cls) -> None:
    while cls.running:
      try:
        task_data: TaskData = await wait_for(fut=cls.task_queue.get(), timeout=0.5)
        task: Task[None] = create_task(coro=cls._process_task_wrapper(task_data=task_data))
        cls.active_tasks.add(task)
        task.add_done_callback(cls.active_tasks.discard)
        cls.task_queue.task_done()
      except TimeoutError:
        continue
      except Exception as err:
        logger.error(msg=f"Error in queue worker: {err}")

  @classmethod
  async def _process_task_wrapper(cls, task_data: TaskData) -> None:
    """Wrapper that handles semaphore acquisition for concurrent processing"""
    async with cls.semaphore:
      await cls._process_task(task_data=task_data)

  @classmethod
  async def _process_task(cls, task_data: TaskData) -> None:
    """Process a single task with retry logic"""
    for attempt in range(task_data.max_retries):
      try:
        logger.debug(msg=f"Processing task {task_data.task_id}, attempt {attempt + 1}")
        await task_data.callable()
        logger.debug(msg=f"Task {task_data.task_id} completed successfully")
        return
      except Exception as err:
        logger.error(f"Task {task_data.task_id} failed on attempt {attempt + 1}: {err}")
        if attempt < task_data.max_retries:
          wait_time: int = 2**attempt
          logger.debug(msg=f"Retrying task {task_data.task_id} in {wait_time} seconds...")
          await sleep(delay=wait_time)
        else:
          logger.error(
            msg=f"Task {task_data.task_id} failed after {task_data.max_retries + 1} attempts"
          )


__all__: Final[tuple[str, ...]] = ("Etiquette",)
