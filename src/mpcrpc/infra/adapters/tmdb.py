from mpcrpc.infra.adapters import (
	QueryResult,
	SearchResult
)

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

	async def Search(self, m_file: MediaFile) -> SearchResult:
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

		if m_file.type == "movie" and getattr(m_file, "year", None):

			query_string: str = f"{m_file.title}, {m_file.year}"
			
			response: str = await self._client.get(
				TMDB.BASE_URL
				+ f"/search/multi?query={urllib.parse.quote(query_string)}&include_adult=true&language=en-US&page=1"
			)

		# this catch series and movie files without a year
		else:
			
			response: str = await self._client.get(
				TMDB.BASE_URL
				+ f"/search/multi?query={urllib.parse.quote(m_file.title)}&include_adult=true&language=en-US&page=1"
			)

		if response == "{}":
			return None
		
		j_resp: Any = json.loads(response)

		# made this to keep a standard
		# between adapters.
		_type: str = j_resp.get("results")[0].get("media_type").replace("tv", "series")

		return SearchResult(
			type=_type,
			id=j_resp.get("results")[0].get("id")
		)

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

		return QueryResult(
			director = director,
			poster = TMDB.IMAGE_URL + j_resp.get("poster_path"),
			title = j_resp.get("original_title"),
			# needed because TMDB api release date format is,
			# for example, "release_date": "1969-02-12"
			year = j_resp.get("release_date").split("-")[0],
		)