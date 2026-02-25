from mpcrpc.core.events import PlaybackSessionUpdated, PlaybackFileUpdated
from mpcrpc.core.models import PlaybackSession, PlaybackFile
from mpcrpc.infra import HttpClient, EventBus
from mpcrpc.utils import Cache, Regex

class MPC:
	"""
	Client interface for interacting with an MPC HTTP instance.
	"""

	def __init__(self, event_bus: EventBus, poll_interval: int, port: int = 13579) -> None:
		"""
		Initialize the MPC client.

		Args:
			port (int):
				Port where the MPC web interface is running.
		"""

		self._poll_interval: int = poll_interval
		self._client: HttpClient = HttpClient()
		self._event_bus: EventBus = event_bus
		self._cache: Cache = Cache()

		self.port: int = port
	
	async def Variables(self) -> None:
		"""
		Fetch current playback session from MPC variables endpoint.
		"""

		response: str = await self._client.get(
			f"localhost:{self.port}/variables.html"
		)

		p_data: dict = Regex.Variables(response)

		p_session: PlaybackSession = PlaybackSession(p_data)
		p_file: PlaybackFile = PlaybackFile(p_data)

		c_session: PlaybackSession = self._cache.get("c_session")
		c_file: PlaybackFile = self._cache.get("c_file")

		# Checks if there is a previous session cached.
		c_session_exists = (
			c_session is not None
		)

		# Checks if the playback position has
		# jumped forward more than the poll interval
		# plus a tolerance of 1500 ms, or if 
		# the playback position got seeked back.
		p_pos_seeked = (
			c_session is not None
			and (
				p_session.pos - c_session.pos >= self._poll_interval + 1500
				or p_session.pos < c_session.pos		
			)
		)

		# Checks if the state of the session
		# (playing/paused/etc.) has changed.
		p_state_changed = (
			c_session is not None
			and (
				c_session.state != p_session.state
			)
		)

		# If there is no previous cached session, or
		# the playback position got seeked, or
		# the session state has changed,
		# then update cache and publish event.
		if not c_session_exists or p_pos_seeked or p_state_changed:
			
			# idk of the atomicity of this, too lazy to test :p
			self._cache.put("c_session", p_session)

			return await self._event_bus.publish(
				PlaybackSessionUpdated(p_session)
			)

		# checks if a cached PlaybackFile exists,
		# if it exists, check if the current
		# is equal to the cached one,
		# then update cache and publish event.
		if not c_file or c_file != p_file:

			self._cache.put("c_file", p_file)

			return await self._event_bus.publish(
				PlaybackFileUpdated(p_file)
			)