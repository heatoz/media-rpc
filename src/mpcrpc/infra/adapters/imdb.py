from mpcrpc.infra import HttpClient
import urllib.parse, json

class Imdb:
	"""
	Wrapper around some IMDB API methods.
	"""

	# GET https://api.imdbapi.dev/search/titles?query=
	@staticmethod
	async def Titles(name: str) -> str | None:
		"""
		Searches a title from IMDB using the Titles endpoint.

		Args:
			name (str):
				The title name.

		Returns:
			str:
				The id of the first result from the query.
			None:
				If the query returns no results.
		"""

		client: HttpClient = HttpClient()
		
		response: str = await client.get(
			f"https://api.imdbapi.dev/search/titles?query={urllib.parse.quote(name)}"
		)

		return json.loads(response).get("titles")[0]
	