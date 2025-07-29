"""Aioimmic library."""

from __future__ import annotations

from aiohttp.client import ClientSession

from .albums import ImmichAlbums
from .api import ImmichApi
from .assets import ImmichAssests
from .people import ImmichPeople
from .search import ImmichSearch
from .server import ImmichServer
from .tags import ImmichTags
from .users import ImmichUsers


class Immich:
    """Immich instance."""

    __slots__ = (
        "api",
        "albums",
        "assets",
        "people",
        "search",
        "server",
        "tags",
        "users",
    )

    api: ImmichApi
    albums: ImmichAlbums
    assets: ImmichAssests
    people: ImmichPeople
    search: ImmichSearch
    server: ImmichServer
    tags: ImmichTags
    users: ImmichUsers

    def __init__(
        self,
        aiohttp_session: ClientSession,
        api_key: str,
        host: str,
        port: int = 2283,
        use_ssl: bool = True,
        device_id: str = "python",
    ) -> None:
        """Immich instace init."""
        self.api = ImmichApi(aiohttp_session, api_key, device_id, host, port, use_ssl)

        self.albums = ImmichAlbums(self.api)
        self.assets = ImmichAssests(self.api)
        self.people = ImmichPeople(self.api)
        self.search = ImmichSearch(self.api)
        self.server = ImmichServer(self.api)
        self.tags = ImmichTags(self.api)
        self.users = ImmichUsers(self.api)
