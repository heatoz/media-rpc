import aiohttp

class HttpClient:
	"""
	Asynchronous HTTP client interface based on the requests library.
	"""

	def __init__(self, headers: dict | None = None, cookies: dict | None = None) -> None:
		"""
		Initialize an HttpClient instance.

		Args:
			headers (dict, optional):
				Optional HTTP headers to include in
				all requests. Defaults to None.

			cookies (Cookies, optional):
				Optional Cookies object to include
				in all requests. Defaults to None.

		Attributes:
			session (requests.Session):
				A persistent requests session object
				used for all HTTP requests.
		"""

		self.session: aiohttp.ClientSession = aiohttp.ClientSession(
			headers = headers,
			cookies = cookies
		)

	async def get(self, path: str) -> aiohttp.ClientResponse:
		"""
		Perform a synchronous HTTP GET request.

		Args:
			path (str):
				The URL to send the GET request to.

		Returns:
			aiohttp.ClientResponse:
				The aiohttp ClientResponse object.
		"""

		r: aiohttp.ClientResponse = await self.session.get(
			path
		)

		return r

	async def post(self, path: str, data: dict) -> aiohttp.ClientResponse:
		"""
		Perform a synchronous HTTP POST request with JSON-encoded data.

		Args:
			path (str):
				The URL to send the POST request to.

			data (dict):
				The payload to send as JSON in the POST body.

		Returns:
			aiohttp.ClientResponse:
				The aiohttp ClientResponse object.
		"""

		r: aiohttp.ClientResponse = await self.session.post(
			path,
			data=data
		)

		return r

	async def close(self) -> None:
		"""
		Close the underlying requests session.
		"""

		await self.session.close()