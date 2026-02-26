from mpcrpc.infra import HttpClient
import urllib.parse, json
from typing import Any

class IMDB:
	"""
	Adapter for the IMDB API methods.
	"""

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

	async def Search(self, name: str) -> str | None:
		"""
		Searches a title from IMDB.

		GET https://api.imdbapi.dev/search/titles?query=

		Note:
			Currently using api.imdbapi.dev for the requests,
			maybe i'll change this on future.

		Args:
			name (str):
				The title name.

		Returns:
			str:
				The id of the first result from the search.
			None:
				If the query returns no results.
		"""

		response: str = await self._client.get(
			f"https://api.imdbapi.dev/search/titles?query={urllib.parse.quote(name)}&limit=1"
		)

		return json.loads(response).get("titles")[0].get("id")
	
	async def Query(self, mid: str) -> dict[str, str]:
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
			f"https://api.imdbapi.dev/titles/{mid}"
		)

		j_resp: Any = json.loads(response)

		# idk if this is just a bloat but made this
		# to keep a good standard between all
		# adapters return values.
		# Note: didn't do a replacement on movies also
		# because their type, on IMDB, already comes as 'movie'.
		_type = j_resp.get("type").replace("tvSeries", "series")

		return {
			"director": j_resp.get("directors")[0].get("displayName"),
			"poster": j_resp.get("primaryImage").get("url"),
			"title": j_resp.get("primaryTitle"),
			"year": j_resp.get("startYear"),
			"type": _type
		}