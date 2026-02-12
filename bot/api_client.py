import aiohttp
from typing import List, Dict, Optional
from config import API_BASE_URL


class TodoAPIClient:
    """Client for interacting with Django REST API."""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_or_create_user(self, telegram_id: int, username: str) -> Optional[Dict]:
        """Get or create user based on Telegram ID."""
        # For simplicity, we'll use telegram_id as Django user_id
        # In production, you'd want proper user management
        try:
            async with self.session.get(f"{self.base_url}/users/{telegram_id}/") as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception:
            pass
        return {'id': telegram_id, 'username': username}
    
    async def get_tasks(self, user_id: int) -> List[Dict]:
        """Get all tasks for a user."""
        try:
            async with self.session.get(
                f"{self.base_url}/tasks/my_tasks/",
                params={'user_id': user_id}
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print(f"Error fetching tasks: {e}")
        return []
    
    async def create_task(self, task_data: Dict) -> Optional[Dict]:
        """Create a new task."""
        try:
            async with self.session.post(
                f"{self.base_url}/tasks/",
                json=task_data
            ) as resp:
                if resp.status == 201:
                    return await resp.json()
        except Exception as e:
            print(f"Error creating task: {e}")
        return None
    
    async def get_categories(self) -> List[Dict]:
        """Get all categories."""
        try:
            async with self.session.get(f"{self.base_url}/categories/") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return data.get('results', data) if isinstance(data, dict) else data
        except Exception as e:
            print(f"Error fetching categories: {e}")
        return []
