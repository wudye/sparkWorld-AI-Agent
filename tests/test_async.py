
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

# 标记这个模块中的所有测试都是异步的
pytestmark = pytest.mark.asyncio

"""
class TestAsyncOperations:

    async def test_async_simple(self):

        async def async_add(a: int, b: int) -> int:
            await asyncio.sleep(0.1)  # 模拟异步操作
            return a + b

        result = await async_add(2, 3)
        assert result == 5

    async def test_async_with_exception(self):

        async def async_raise_error():
            await asyncio.sleep(0.1)
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            await async_raise_error()

    async def test_async_timeout(self):

        async def slow_operation():
            await asyncio.sleep(2)  # 2秒操作
            return "done"

        # 使用 asyncio.timeout 设置超时
        try:
            async with asyncio.timeout(1.0):
                result = await slow_operation()
            assert False, "Should have timed out"
        except TimeoutError:
            pass  # 预期的超时

    async def test_async_client(self):
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/")

        assert response.status_code == 200
        assert "message" in response.json()
"""