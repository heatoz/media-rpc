from media_rpc.infra.adapters import SearchResult, QueryResult
from media_rpc.infra import HttpClient
from media_rpc.utils import MediaFile

import urllib.parse
import json

from typing import Any


class IMDB:
    """
    Adapter for the IMDB API methods.
    """

    BASE_URL: str = "https://api.imdbapi.dev"

    def __init__(self):
        """
        Initialize a IMDB adapter object.

        Attributes:
                client (HttpClient):
                        Class HTTP Session for requests.
        """

        self._client: HttpClient = HttpClient(headers={"Accept": "application/json"})

        self.m_file: MediaFile | None = None

    async def __search(self) -> SearchResult | None:
        """
        Search a title from IMDB.

        GET https://api.imdbapi.dev/search/titles?query=

        Note:
                Currently using api.imdbapi.dev for the requests,
                maybe i'll change this on future.

        Returns:
                SearchResult:
                        A data class containing the search result.

                None:
                        If the search results on nothing.
        """

        # if the media file has its year,
        # use it to do a better query.
        # TODO: make a safety check of year + 1 and year - 1
        # when the filename title + year returns nothing.
        if self.m_file.type == "movie" and getattr(self.m_file, "year", None):
            query_string: str = f"{self.m_file.title} {self.m_file.year}"

            j_resp: Any = json.loads(
                await self._client.get(
                    IMDB.BASE_URL
                    + f"/search/titles?query={urllib.parse.quote(query_string)}&limit=1"
                )
            )

        # this will catch movies without a year and series.
        else:
            j_resp: Any = json.loads(
                await self._client.get(
                    IMDB.BASE_URL
                    + f"/search/titles?query={urllib.parse.quote(self.m_file.title)}&limit=1"
                )
            )

        if not j_resp.get("titles"):
            return None

        return SearchResult(
            id = j_resp.get("titles")[0].get("id")
        )

    async def __query(self, search_r: SearchResult) -> QueryResult:
        """
        Queries a title details from its id.

        GET https://api.imdbapi.dev/titles/

        Note:
                Currently using api.imdbapi.dev for the requests,
                maybe i'll change this on future.

        Args:
                search_r (SearchResult):
                        The search result.

        Returns:
                QueryResult:
                        Contains the necessary title data
                        for initializing a Movie or Series object.
        """

        # it's only one endpoint for both series and movies so...
        j_resp: Any = json.loads(
            await self._client.get(IMDB.BASE_URL + f"/titles/{search_r.id}")
        )

        title: str = j_resp.get("originalTitle") or j_resp.get("primaryTitle")
        # sadly, api.imdbapi.dev doesn't support custom seasons posters :(
        poster: str = j_resp.get("primaryImage").get("url")

        if self.m_file.type == "episode":
            season: str = getattr(self.m_file, "season", None) or "1"

            j_resp: Any = json.loads(
                await self._client.get(
                    IMDB.BASE_URL + f"/titles/{search_r.id}/episodes?season={season}"
                )
            )
            episode_title: str | None = next(
                (
                    ep["title"]
                    for ep in j_resp.get("episodes", [])
                    if ep["episodeNumber"] == int(self.m_file.episode)
                ),
                None,
            )

            return QueryResult(
                title = title,
                poster = poster,
                episode_title = episode_title,
            )

        if self.m_file.type == "movie":
            director: str = j_resp.get("directors")[0].get("displayName")
            year: str = j_resp.get("startYear")

            return QueryResult(
                director=director,
                poster=poster,
                title=title,
                year=year,
            )

    async def Fetch(self, m_file: MediaFile) -> QueryResult | None:
        """
        Wrapper around Search and Query private methods.

        Note:
            Made only so the caller can avoid calling two
            methods and passing m_file two times.

        Args:
            m_file
        """

        self.m_file: MediaFile = m_file

        search_r: SearchResult = await self.__search()
        if search_r is None:
            return None

        return await self.__query(search_r)
