import asyncio
from .utils import setup_logger
import httpx
from typing import Optional
from .utils import BASE_URL , AUTH_TOKEN

logger = setup_logger("channel-bot", level="INFO")



class ChannelAPIClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.headers = {'Content-Type': 'application/json'}
        if token:
            self.headers['Authorization'] = f'Bearer {token}'
        self.client = httpx.AsyncClient(headers=self.headers)

    async def close(self):
        await self.client.aclose()

    # ===== ChannelRewriteRule Methods =====
    async def list_channel_rules(self, is_active: Optional[bool] = None):
        url = f"{self.base_url}/channel-rules/"
        params = {}
        if is_active is not None:
            params['is_active'] = str(is_active).lower()
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def retrieve_channel_rule(self, pk: int):
        url = f"{self.base_url}/channel-rules/{pk}/"
        resp = await self.client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def create_channel_rule(
        self,
        is_active: bool = True,
        join_url_source_channel: str = 'https://t.me/',
        join_url_destination_channel: str = 'https://t.me/',
        source_channel_name: Optional[str] = None,
        source_channel_id: Optional[str] = None,
        destination_channel_name: Optional[str] = None,
        destination_channel_id: Optional[str] = None,
        message_signature: Optional[str] = None,
        model_choice: str = 'gpt-4o-mini',
        prompt: Optional[str] = None,
        replace_words_text: Optional[str] = None,
        must_include_words_text: Optional[str] = None,
        ignore_words_text: Optional[str] = None,
    ):
        url = f"{self.base_url}/channel-rules/"
        data = {
            "is_active": is_active,
            "join_url_source_channel": join_url_source_channel,
            "join_url_destination_channel": join_url_destination_channel,
            "source_channel_name": source_channel_name,
            "source_channel_id": source_channel_id,
            "destination_channel_name": destination_channel_name,
            "destination_channel_id": destination_channel_id,
            "message_signature": message_signature,
            "model_choice": model_choice,
            "prompt": prompt,
            "replace_words_text": replace_words_text,
            "must_include_words_text": must_include_words_text,
            "ignore_words_text": ignore_words_text,
        }
        data = {k: v for k, v in data.items() if v is not None}
        resp = await self.client.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    async def update_channel_rule(self, pk: int, **kwargs):
        url = f"{self.base_url}/channel-rules/{pk}/"
        data = {k: v for k, v in kwargs.items() if v is not None}
        resp = await self.client.put(url, json=data)
        resp.raise_for_status()
        return resp.json()

    async def partial_update_channel_rule(self, pk: int, **kwargs):
        url = f"{self.base_url}/channel-rules/{pk}/"
        data = {k: v for k, v in kwargs.items() if v is not None}
        resp = await self.client.patch(url, json=data)
        resp.raise_for_status()
        return resp.json()

    async def delete_channel_rule(self, pk: int):
        url = f"{self.base_url}/channel-rules/{pk}/"
        resp = await self.client.delete(url)
        resp.raise_for_status()
        return resp.status_code == 204

    # ===== RewrittenPost Methods =====
    async def list_rewritten_posts(self, search: Optional[str] = None):
        url = f"{self.base_url}/rewritten-posts/"
        params = {}
        if search:
            params['search'] = search
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

    async def retrieve_rewritten_post(self, pk: int):
        url = f"{self.base_url}/rewritten-posts/{pk}/"
        resp = await self.client.get(url)
        resp.raise_for_status()
        return resp.json()

    async def create_rewritten_post(
        self,
        rule: Optional[int] = None,
        message_type: Optional[str] = None,
        original_message_id: int = None,
        rewritten_message_id: Optional[int] = None,
        original_text: str = None,
        rewritten_text: str = None,
        error_message: Optional[str] = None,
    ):
        url = f"{self.base_url}/rewritten-posts/"
        data = {
            "rule": rule,
            "message_type": message_type,
            "original_message_id": original_message_id,
            "rewritten_message_id": rewritten_message_id,
            "original_text": original_text,
            "rewritten_text": rewritten_text,
            "error_message": error_message,
        }
        data = {k: v for k, v in data.items() if v is not None}
        resp = await self.client.post(url, json=data)
        resp.raise_for_status()
        return resp.json()

    async def update_rewritten_post(self, pk: int, **kwargs):
        url = f"{self.base_url}/rewritten-posts/{pk}/"
        data = {k: v for k, v in kwargs.items() if v is not None}
        resp = await self.client.put(url, json=data)
        resp.raise_for_status()
        return resp.json()

    async def partial_update_rewritten_post(self, pk: int, **kwargs):
        url = f"{self.base_url}/rewritten-posts/{pk}/"
        data = {k: v for k, v in kwargs.items() if v is not None}
        resp = await self.client.patch(url, json=data)
        resp.raise_for_status()
        return resp.json()

    async def delete_rewritten_post(self, pk: int):
        url = f"{self.base_url}/rewritten-posts/{pk}/"
        resp = await self.client.delete(url)
        resp.raise_for_status()
        return resp.status_code == 204


print(BASE_URL)
print(AUTH_TOKEN)
con = ChannelAPIClient(base_url=BASE_URL , token=AUTH_TOKEN)
