from abc import ABC
from typing import Final

from .core.client_factory import HttpxFactory
from .core.context import RequestContext
from .core.enums import Provider, ClientType
from .utils import get_from_env

OASIS_PROXY_URL: Final[str] = "OASIS_PROXY_URL"


class ProviderBase(ABC):
    """
    공급자 래퍼들의 공통 부모

    * RequestContext & HttpxFactory 인스턴스 생성/보관
    * protected 멤버 `_ctx`, `_httpx` 노출
    """

    def __init__(
        self,
        *,
        user_id: str,
        workspace_id: str,
        tenant_id: str,
        provider: Provider,
        client_type: ClientType = ClientType.SDK,
        plugin_name: str | None = None,
        user_ip: str | None = None,
        root_id: str | None = None,
        audit_state: bool = True,
    ) -> None:
        self._ctx = RequestContext(
            user_id=user_id,
            plugin_name=plugin_name,
            workspace_id=workspace_id,
            tenant_id=tenant_id,
            provider=provider,
            client_type=client_type,
            user_ip=user_ip,
            root_id=root_id,
            audit_state=audit_state,
        )
        self._httpx = HttpxFactory(self._ctx)

    @staticmethod
    def _resolve_base_url(url: str | None) -> str:
        return url or get_from_env(OASIS_PROXY_URL)
