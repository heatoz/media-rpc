from mpcrpc.infra.adapters import SearchResult, QueryResult

from mpcrpc.infra import HttpClient
from mpcrpc.utils import MediaFile

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

    async def __Search(self, m_file: MediaFile) -> SearchResult | None:
        """
        Search a title from IMDB.

        GET https://api.imdbapi.dev/search/titles?query=

        Note:
                Currently using api.imdbapi.dev for the requests,
                maybe i'll change this on future.

        Args:
                m_file (MediaFile):
                        A parsed file object.

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
        if m_file.type == "movie" and getattr(m_file, "year", None):
            query_string: str = f"{m_file.title} {m_file.year}"

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
                    + f"/search/titles?query={urllib.parse.quote(m_file.title)}&limit=1"
                )
            )

        if not j_resp:
            return None

        return SearchResult(id=j_resp.get("titles")[0].get("id"))

    async def __Query(self, m_file: MediaFile, search_r: SearchResult) -> QueryResult:
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

        # sadly, api.imdbapi.dev doesn't support custom seasons posters :(
        poster: str = j_resp.get("primaryImage").get("url")
        title: str = j_resp.get("originalTitle") or j_resp.get("primaryTitle")

        if m_file.type == "episode":
            # give preference to the original titles.
            season: str = getattr(m_file, "season", None) or "1"

            j_resp: Any = json.loads(
                await self._client.get(
                    IMDB.BASE_URL + f"/titles/{search_r.id}/episodes?season={season}"
                )
            )
            episode_title: str | None = next(
                (
                    ep["title"]
                    for ep in j_resp.get("episodes", [])
                    if ep["episodeNumber"] == int(m_file.episode)
                ),
                None,
            )

            return QueryResult(title=title, poster=poster, episode_title=episode_title)

        if m_file.type == "movie":
            # give preference to the original titles.
            director: str = j_resp.get("directors")[0].get("displayName")
            year: str = j_resp.get("startYear")

            return QueryResult(director=director, poster=poster, title=title, year=year)

    async def Fetch(self, m_file: MediaFile) -> QueryResult | None:
        """
        Wrapper around Search and Query private methods.

        Note:
            Made only so the caller can avoid calling two
            methods and passing m_file two times.

        Args:
            m_file
        """
        search_r: SearchResult = await self.__Search(m_file)
        if search_r is None:
            return None

        return await self.__Query(m_file, search_r)
