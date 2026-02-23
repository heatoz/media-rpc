from mpcrpc.core.models.mpc import PlaybackSession
from mpcrpc.infra import HttpClient

class MPC:
	"""
	Client interface for interacting with an MPC HTTP instance.
	"""

	def __init__(self, port: int) -> None:
		"""
		Initialize the MPC client.

		Args:
			port (int):
				Port where the MPC web interface is running.
		"""

		self._client: HttpClient = HttpClient()
		self.port: int = port
	
	async def Variables(self) -> PlaybackSession:
		"""
		Fetch current playback session from MPC variables endpoint.

		Returns:
			PlaybackSession:
				Parsed playback session data.
		"""

		response: str = await self._client.get(
			f"localhost:{self.port}/variables.html"
		)

		return PlaybackSession(response)