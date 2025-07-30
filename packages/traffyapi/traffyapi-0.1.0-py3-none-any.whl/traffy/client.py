import aiohttp

from .models import GetTraffyTasksResponse, CheckTraffyTaskResponse
from .exceptions import TraffyAPIError


class TraffyAPI:
    BASE_URL = "https://api.traffy.site/v1/mixer/bot"

    def __init__(self, resource_id: str, session: aiohttp.ClientSession = None):
        self.resource_id = resource_id
        self.session = session or aiohttp.ClientSession()

    async def get_tasks(self, telegram_chat_id: str, max_tasks: int = 3) -> GetTraffyTasksResponse:
        url = f"{self.BASE_URL}/pick_tasks"
        params = {
            "resource_id": self.resource_id,
            "telegram_id": telegram_chat_id,
            "max_tasks": max_tasks
        }

        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise TraffyAPIError(f"Error fetching tasks: {response.status}")
            return await response.json()

    async def check_task(self, telegram_chat_id: str, task_id: str) -> CheckTraffyTaskResponse:
        url = f"{self.BASE_URL}/check_completion"
        params = {
            "resource_id": self.resource_id,
            "telegram_id": telegram_chat_id,
            "task_id": task_id
        }

        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise TraffyAPIError(f"Error checking task: {response.status}")
            return await response.json()

    async def close(self):
        await self.session.close()
