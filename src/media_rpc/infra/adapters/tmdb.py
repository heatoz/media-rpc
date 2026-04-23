from media_rpc.infra.adapters import QueryResult, SearchResult

from media_rpc.infra import HttpClient
from media_rpc.utils import MediaFile

from typing import Any

import urllib.parse
import json


class TMDB:
    """
    Adapter for the TMDB API methods.
    """

    IMAGE_URL: str = "https://image.tmdb.org/t/p/original"
    BASE_URL: str = "https://api.themoviedb.org/3"

    def __init__(self, token: str):
        """
        Initialize a TMDB adapter object.

        Args:
                        token (str):
                                        A TMDB API token.

        Attributes:
                        client (HttpClient):
                                        Class HTTP Session for requests.
        """

        self._client: HttpClient = HttpClient(
            headers={"Accept": "application/json", "Authorization": f"Bearer {token}"}
        )

        self.m_file: MediaFile | None = None

    async def __search(self) -> SearchResult | None:
        """
        Search a title from TMDB.

        Returns:
                SearchResult:
                        A data class containing the search result.

                None:
                        If the search results on nothing.
        """

        # it wasn't possible to do a title + year more
        # detailed check on tmdb because its search doesn't
        # support it. Idk of any solution.
        if self.m_file.type == "episode":
            response: str = await self._client.get(
                TMDB.BASE_URL
                + f"/search/tv?query={urllib.parse.quote(self.m_file.title)}&include_adult=true&language=en-US&page=1"
            )

        if self.m_file.type == "movie":
            response: str = await self._client.get(
                TMDB.BASE_URL
                + f"/search/movie?query={urllib.parse.quote(self.m_file.title)}&include_adult=true&language=en-US&page=1"
            )

        j_resp: Any = json.loads(response)

        # here this check needs to happen after json loading
        # the response because tmdb doesn't return just a empty {}.
        if j_resp.get("total_results") == 0:
            return None

        return SearchResult(
            id = j_resp.get("results")[0].get("id")
        )

    async def __query(self, search_r: SearchResult) -> QueryResult:
        """
        Queries a title details from its id.

        Args:
                search_r (SearchResult):
                        The search result.

        Returns:
                QueryResult:
                        Contains the necessary title data
                        for initializing a Movie or Series object.
        """

        # uses the m_file type to do checks to avoid
        # any mismatching errors with guessit results.
        if self.m_file.type == "episode":
            j_resp: Any = json.loads(
                await self._client.get(
                    TMDB.BASE_URL + f"/tv/{search_r.id}&language=en-US"
                )
            )

            title: str = j_resp.get("original_name") or j_resp.get("name")
            season: str = getattr(self.m_file, "season", None) or "1"
            # this will give priority to the season poster
            poster_path = next(
                (
                    s["poster_path"]
                    for s in j_resp.get("seasons", [])
                    if s["season_number"] == int(season)
                ),
                None,
            ) or j_resp.get("poster_path")
            poster: str | None = TMDB.IMAGE_URL + poster_path if poster_path else None

            # queries the episode to get the episode title.
            j_resp: Any = json.loads(
                await self._client.get(
                    TMDB.BASE_URL
                    + f"/tv/{search_r.id}/season/{season}/episode/{self.m_file.episode}"
                )
            )
            episode_title: str = j_resp.get("original_name") or j_resp.get("name")

            return QueryResult(
                title = title,
                poster = poster,
                episode_title = episode_title
            )

        if self.m_file.type == "movie":
            j_resp: Any = json.loads(
                await self._client.get(
                    TMDB.BASE_URL
                    + f"/movie/{search_r.id}?append_to_response=credits&language=en-US"
                )
            )

            poster: str = TMDB.IMAGE_URL + j_resp.get("poster_path")
            year: str = j_resp.get("release_date").split("-")[0]
            title: str = j_resp.get("original_title")
            director: str = next(
                (
                    member["name"]
                    for member in j_resp.get("credits").get("crew")
                    if member["job"] == "Director"
                ),
                None,
            )

            return QueryResult(
                director = director,
                poster = poster,
                title = title,
                year = year
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
