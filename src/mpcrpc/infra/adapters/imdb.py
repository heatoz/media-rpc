from mpcrpc.infra import HttpClient
from mpcrpc.utils import Filename
import urllib.parse, json
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

	async def Search(self, filename: Filename) -> dict[str, str] | None:
		"""
		Searches a title from IMDB.

		GET https://api.imdbapi.dev/search/titles?query=

		Note:
			Currently using api.imdbapi.dev for the requests,
			maybe i'll change this on future.

		Args:
			filename (Filename):
				The file parsed Filename object.

		Returns:
			dict:
				Returns the search result id
				and its type.
			None:
				If the search returns no results.
		"""

		if filename.type == "movie":

			if filename.year:

				query_string: str = f"{filename.title} {filename.year}"

				response: str = await self._client.get(
					IMDB.BASE_URL + f"/search/titles?query={urllib.parse.quote(query_string)}&limit=1"
				)

		else:

			response: str = await self._client.get(
				IMDB.BASE_URL + f"/search/titles?query={urllib.parse.quote(filename.title)}&limit=1"
			)

		if response == "{}":
			return None

		j_resp: Any = json.loads(response)

		# did this to keep a standard between
		# adapters, maybe there's a better solution.
		_type: str = j_resp.get("titles")[0].get("type").replace("tvSeries", "series")

		return {
			"type": _type,
			"id": j_resp.get("titles")[0].get("id")
		}
	
	async def Query(self, search_r: dict[str, str]) -> dict[str, str]:
		"""
		Queries a title details from its id.

		GET https://api.imdbapi.dev/titles/

		Note:
			Currently using api.imdbapi.dev for the requests,
			maybe i'll change this on future.

		Args:
			mid (str):
				The media id.
		
		Returns:
			dict:
				Contains the necessary title data
				for initializing a Movie or Series object.
		"""

		response: str = await self._client.get(
			IMDB.BASE_URL + f"/titles/{search_r["id"]}"
		)

		j_resp: Any = json.loads(response)

		return {
			"director": j_resp.get("directors")[0].get("displayName"),
			"poster": j_resp.get("primaryImage").get("url"),
			"title": j_resp.get("originalTitle"),
			"year": j_resp.get("startYear")
		}