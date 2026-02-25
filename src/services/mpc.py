from mpcrpc.core.events import PlaybackSessionUpdated, PlaybackFileUpdated
from mpcrpc.core.models import PlaybackSession, PlaybackFile
from mpcrpc.infra import HttpClient, EventBus
from mpcrpc.utils import Cache, Parser
from typing import Any

class MPC:
	"""
	Client interface for interacting with an MPC HTTP instance.
	"""

	def __init__(self, event_bus: EventBus, port: int = 13579) -> None:
		"""
		Initialize the MPC client.

		Args:
			port (int):
				Port where the MPC web interface is running.
		"""

		self._client: HttpClient = HttpClient()
		self._cache: Cache = Cache()
		self._event_bus = event_bus

		self.port: int = port
	
	async def Variables(self) -> None:
		"""
		Fetch current playback session from MPC variables endpoint.
		"""

		response: str = await self._client.get(
			f"localhost:{self.port}/variables.html"
		)

		p_data: dict = Parser.Variables(response)

		p_session: PlaybackSession = PlaybackSession(p_data)
		p_file: PlaybackFile = PlaybackFile(p_data)

		c_session: Any = self._cache.get("c_session")
		c_file: Any = self._cache.get("c_file")

		# checks if a cached PlaybackSession exists
		# and if it exists, check if the current
		# is equal to the cached one.
		if not c_session or c_session != p_session:
			
			# idk of the atomicity of this, too lazy to test :p
			self._cache.put("c_session", p_session)

			return await self._event_bus.publish(
				PlaybackSessionUpdated(p_session)
			)

		# checks if a cached PlaybackFile exists
		# and if it exists, check if the current
		# is equal to the cached one.
		if not c_file or c_file != p_file:

			self._cache.put("c_file", p_file)

			return await self._event_bus.publish(
				PlaybackFileUpdated(p_file)
			)