from media_rpc.infra.adapters import SearchResult, QueryResult
from media_rpc.infra import HttpClient
from media_rpc.utils import MediaFile

import urllib.parse
import json

from typing import Any

class AniList:

    SEARCH_QUERY: str = """
        query ($search: String) {
        Media (search: $search, type: ANIME, sort: SEARCH_MATCH) {
            id
            format
            title {
            romaji
            english
            native
            }
            coverImage {
            extraLarge
            }
            startDate {
            year
            }
            staff(perPage: 1, sort: RELEVANCE) {
            edges {
                role
                node {
                name { full }
                }
            }
            }
        }
        }
    """

    BASE_URL: str = "https://graphql.anilist.co"

    def __init__(self):
        
        self._client = HttpClient(
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
        })

        self.m_file: MediaFile | None = None

    async def __search(self) -> SearchResult:

        j_resp: Any = json.loads(await self._client.post(
            AniList.BASE_URL,
            data = {
                "query": AniList.SEARCH_QUERY,
                "variables": {
                    "search": self.m_file.title
                }
            }
        ))


    async def __query(self, search_r: SearchResult) -> QueryResult:
        ...

    async def Fetch(self, m_file: MediaFile) -> QueryResult:
        ...
