"""Microsoft Graph API client -- singleton wrapper around the msgraph SDK."""

from __future__ import annotations

import threading

from azure.identity.aio import ClientSecretCredential
from msgraph import GraphServiceClient

from app.config import get_settings

_SCOPES = ["https://graph.microsoft.com/.default"]


class GraphAPIClient:
    """Singleton that holds a configured :class:`GraphServiceClient`.

    Usage::

        client = GraphAPIClient.get_client()
        user = await client.users.by_user_id("...").get()

    Call :meth:`close` during application shutdown to release the underlying
    credential / HTTP resources.
    """

    _instance: GraphServiceClient | None = None
    _credential: ClientSecretCredential | None = None
    _lock = threading.Lock()

    @classmethod
    def get_client(cls) -> GraphServiceClient:
        """Return the singleton :class:`GraphServiceClient`, creating it on first call."""
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    settings = get_settings()
                    cls._credential = ClientSecretCredential(
                        tenant_id=settings.azure_tenant_id,
                        client_id=settings.azure_client_id,
                        client_secret=settings.azure_client_secret,
                    )
                    cls._instance = GraphServiceClient(
                        credentials=cls._credential,
                        scopes=_SCOPES,
                    )
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        """Dispose of the credential and reset the singleton.

        Should be called once during application shutdown.
        """
        with cls._lock:
            if cls._credential is not None:
                await cls._credential.close()
                cls._credential = None
            cls._instance = None
