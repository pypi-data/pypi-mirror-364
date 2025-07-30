#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/src/etiquette/_types.py
# VERSION:     0.0.1
# CREATED:     2025-07-23 14:20
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION:
#
# HISTORY:
# *************************************************************

### Standard packages ###
from dataclasses import dataclass
from typing import Any, Callable, Final
from uuid import UUID


@dataclass
class TaskData:
  callable: Callable[..., Any]
  task_id: UUID
  max_retries: int = 3


__all__: Final[tuple[str, ...]] = ("TaskData",)
