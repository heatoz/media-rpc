from mpcrpc.infra.adapters import QueryResult, SearchResult

from mpcrpc.infra import HttpClient
from mpcrpc.utils import MediaFile

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

    async def Search(self, m_file: MediaFile) -> SearchResult | None:
        """
        Search a title from TMDB.

        Args:
                m_file (MediaFile):
                        A parsed media file object.

        Returns:
                SearchResult:
                        A data class containing the search result.

                None:
                        If the search results on nothing.
        """

        # it wasn't possible to do a title + year more
        # detailed check on tmdb because its search doesn't
        # support it. Idk of any solution.
        response: str = await self._client.get(
            TMDB.BASE_URL
            + f"/search/multi?query={urllib.parse.quote(m_file.title)}&include_adult=true&language=en-US&page=1"
        )

        j_resp: Any = json.loads(response)

        # here this check needs to happen after json loading
        # the response because tmdb doesn't return just a empty {}.
        if j_resp.get("total_results") == 0:
            return None

        # made this to keep a standard
        # between adapters.
        _type: str = j_resp.get("results")[0].get("media_type").replace("tv", "series")

        return SearchResult(type=_type, id=j_resp.get("results")[0].get("id"))

    async def Query(self, search_r: SearchResult) -> QueryResult:
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

        response: str = await self._client.get(
            TMDB.BASE_URL
            + f"/{search_r.type.replace('series', 'tv')}/{search_r.id}?append_to_response=credits&language=en-US"
        )

        j_resp: Any = json.loads(response)

        # this returns the first Director from the crew.
        director: str = next(
            (
                member["name"]
                for member in j_resp.get("credits").get("crew")
                if member["job"] == "Director"
            ),
            None,
        )

        # this tag differs on movies and series.
        year = j_resp.get("release_date") or j_resp.get("first_air_date")

        return QueryResult(
            director=director,
            poster=TMDB.IMAGE_URL + j_resp.get("poster_path"),
            # this tag differs on movies and series.
            title=j_resp.get("original_title") or j_resp.get("name"),
            year=year.split("-")[0],
        )
