from mpcrpc.infra.adapters import (
	SearchResult,
	QueryResult
)

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

		self._client: HttpClient = HttpClient(
			headers = {
				"Accept": "application/json"
			}
		)

	async def Search(self, m_file: MediaFile) -> SearchResult | None:
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

			response: str = await self._client.get(
				IMDB.BASE_URL
				+ f"/search/titles?query={urllib.parse.quote(query_string)}&limit=1"
			)

		# this will catch movies without a year and series.
		else:

			response: str = await self._client.get(
				IMDB.BASE_URL
				+ f"/search/titles?query={urllib.parse.quote(m_file.title)}&limit=1"
			)

		if response == "{}":
			return None

		s_data: dict[str, str] = json.loads(response).get("titles")[0]

		return SearchResult(
			# Made this replacement to keep a standard between adapters.
			type = s_data.get("type").replace("tvSeries", "series"),
			id = s_data.get("id")
		)
	
	async def Query(self, search_r: SearchResult) -> QueryResult:
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

		response: str = await self._client.get(
			IMDB.BASE_URL
			+ f"/titles/{search_r.id}"
		)

		s_data: Any = json.loads(response)

		return QueryResult(
			director = s_data.get("directors")[0].get("displayName"),
			poster = s_data.get("primaryImage").get("url"),
			# Give preference to original titles.
			title = s_data.get("originalTitle") or s_data.get("primaryTitle"),
			year = s_data.get("startYear")
		)