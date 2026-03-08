from mpcrpc.infra.adapters import SearchResult, QueryResult

from mpcrpc.infra import HttpClient
from mpcrpc.utils import MediaFile

import urllib.parse
import json
import re

from typing import Any


class MAL:
    "Adapter for the MyAnimeList API methods."

    BASE_URL: str = "https://api.jikan.moe/v4"

    def __init__(self):
        """
        Initialize a MAL adapter instance.

        Note:
            Currently using jikan for the requests,
            please let me know if there's anything better.
        """

        self._client: HttpClient = HttpClient()

    async def __Search(self, m_file: MediaFile) -> SearchResult | None:
        """
        Search a title from MAL.

        Args:
                m_file (MediaFile):
                        A parsed file object.

        Returns:
                SearchResult:
                        A data class containing the search result.

                None:
                        If the search results on nothing.
        """

        if m_file.type == "episode":
            if getattr(m_file, "season", None) and int(m_file.season) > 1:
                query: str = f"{m_file.title} Season {m_file.season}"

                j_resp: Any = json.loads(
                    await self._client.get(
                        MAL.BASE_URL
                        + f"/anime?q={urllib.parse.quote(query)}&limit=1&type=tv"
                    )
                ).get("data")[0]

            # this is matched for animes with only one season.
            else:
                j_resp: Any = json.loads(
                    await self._client.get(
                        MAL.BASE_URL
                        + f"/anime?q={urllib.parse.quote(m_file.title)}&limit=1&type=tv"
                    )
                ).get("data")[0]

        if m_file.type == "movie":
            j_resp: Any = json.loads(
                await self._client.get(
                    MAL.BASE_URL
                    + f"/anime?q={urllib.parse.quote(m_file.title)}&limit=1&type=movie"
                )
            ).get("data")[0]

        if not j_resp:
            return None

        return SearchResult(id=j_resp.get("mal_id"))

    async def __Query(self, m_file: MediaFile, search_r: SearchResult) -> QueryResult:
        """
        Queries a title details from its id.

        Args:
                m_file(MediaFile):
                        The parsed Media File.
                search_r (SearchResult):
                        The search result.

        Returns:
                QueryResult:
                        Contains the necessary title data
                        for initializing a Movie or Series object.
        """

        # common to both
        j_resp: Any = json.loads(
            await self._client.get(MAL.BASE_URL + f"/anime/{search_r.id}/full")
        ).get("data")

        poster: str = j_resp.get("images").get("jpg").get("large_image_url")
        # remove Season from the end of the title, ugh.
        title: str = re.sub(r" Season \d+$", "", j_resp.get("title"))

        if m_file.type == "episode":
            # matches the correct page for the episode.
            page = (int(m_file.episode) - 1) // 100 + 1

            j_resp: Any = json.loads(
                await self._client.get(
                    MAL.BASE_URL + f"/anime/{search_r.id}/episodes?page={page}"
                )
            ).get("data")

            episode_title: str | None = next(
                (ep["title"] for ep in j_resp if ep["mal_id"] == int(m_file.episode)),
                None,
            )

            return QueryResult(title=title, poster=poster, episode_title=episode_title)

        if m_file.type == "movie":
            year: str = j_resp.get("year")

            j_resp: Any = json.loads(
                await self._client.get(MAL.BASE_URL + f"/anime/{search_r.id}/staff")
            ).get("data")

            # fetches the first director from the list
            director: str | None = next(
                (
                    p["person"]["name"]
                    for p in j_resp.get("data", [])
                    if "Director" in p.get("positions", [])
                ),
                None,
            )

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
