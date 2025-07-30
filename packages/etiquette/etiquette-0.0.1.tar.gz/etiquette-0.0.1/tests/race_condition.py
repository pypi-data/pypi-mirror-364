#!/usr/bin/env python3.9
# coding:utf-8
# Copyright (C) 2025 All rights reserved.
# FILENAME:    ~~/tests/race_condition.py
# VERSION:     0.0.1
# CREATED:     2025-07-24 13:11
# AUTHOR:      Sitt Guruvanich <aekazitt+github@gmail.com>
# DESCRIPTION: Test script to demonstrate race condition when used incorrectly
#
# HISTORY:
# *************************************************************

### Third-party packages ###
from fastapi.testclient import TestClient
from httpx import Response
from pytest import mark

### Local modules ###
from tests import test_client


@mark.asyncio
async def test_safe_counter(test_client: TestClient) -> None:
  """Test to demonstrate race condition prevention on SafeCounter"""
  with test_client as client:
    for i in range(20):
      client.get("/safe-counter")
    response: Response = client.get("/safe-counter")
    assert int(response.text) == 20


@mark.asyncio
async def test_unsafe_counter(test_client: TestClient) -> None:
  """Test to demonstrate race condition on UnsafeCounter"""
  with test_client as client:
    for i in range(20):
      client.get("/unsafe-counter")
    response: Response = client.get("/unsafe-counter")
    assert int(response.text) < 20
