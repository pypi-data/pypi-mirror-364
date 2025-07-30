#!/usr/bin/env python3.9
# coding:utf-8
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
Semaphored background queue for Asynchronous Server Gateway Interface (ASGI) frameworks
"""

### Standard packages ###
from typing import Final

### Local modules ###
from etiquette.core import Etiquette
from etiquette.decorum import Decorum

__all__: Final[tuple[str, ...]] = ("Decorum", "Etiquette")
__version__ = "0.0.1"
