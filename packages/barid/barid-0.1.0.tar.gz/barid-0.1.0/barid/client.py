import httpx
from typing import List
from .ctypes import EmailAddress, EmailID, Limit, Offset, Message
from .models.email import Email, EmailDetails
from .models.response import (
    EmailListResponse,
    EmailDetailsResponse,
    MessageResponse,
    ErrorResponse,
)
from .exceptions import BaridAPIError

BASE_URL = "https://api.barid.site"


class BaridClient:
    def __init__(self, timeout: float = 10.0) -> None:
        self._client: httpx.AsyncClient | None = None
        self._timeout = timeout

    async def __aenter__(self) -> "BaridClient":
        self._client = httpx.AsyncClient(timeout=self._timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()

    async def _handle(self, response: httpx.Response, model):
        data = response.json()
        if not data.get("status", False):
            err = ErrorResponse(**data).error
            raise BaridAPIError(err.name, err.message)
        return model(**data).result

    async def get_emails(
        self, email: EmailAddress, limit: Limit = 10, offset: Offset = 0
    ) -> List[Email]:
        assert self._client is not None, "Client not initialized, use 'async with'"
        url = f"{BASE_URL}/emails/{email}"
        resp = await self._client.get(url, params={"limit": limit, "offset": offset})
        return await self._handle(resp, EmailListResponse)

    async def delete_emails(self, email: EmailAddress) -> Message:
        assert self._client is not None, "Client not initialized, use 'async with'"
        url = f"{BASE_URL}/emails/{email}"
        resp = await self._client.delete(url)
        return (await self._handle(resp, MessageResponse))["message"]

    async def get_email(self, email_id: EmailID) -> EmailDetails:
        assert self._client is not None, "Client not initialized, use 'async with'"
        url = f"{BASE_URL}/inbox/{email_id}"
        resp = await self._client.get(url)
        return await self._handle(resp, EmailDetailsResponse)

    async def delete_email(self, email_id: EmailID) -> Message:
        assert self._client is not None, "Client not initialized, use 'async with'"
        url = f"{BASE_URL}/inbox/{email_id}"
        resp = await self._client.delete(url)
        return (await self._handle(resp, MessageResponse))["message"]
