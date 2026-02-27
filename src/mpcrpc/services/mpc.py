from mpcrpc.core.models import (
	PlaybackSession,
	PlaybackFile,
	PlaybackState
)

from mpcrpc.core.events import (
	PlaybackSessionUpdated,
	PlaybackFileUpdated
)

from mpcrpc.infra import (
	HttpClient,
	EventBus
)

from mpcrpc.utils import (
	Cache,
	Regex
)

import time

class MPC:
	"""
	Client interface for interacting with an MPC HTTP instance.
	"""

	def __init__(self, event_bus: EventBus, port: int = 13579) -> None:
		"""
		Initialize the MPC client.

		Args:
			event_bus (EventBus):
				The Event Bus used by the service.

			port (int):
				Port where the MPC web interface is running.
		"""

		self._client: HttpClient = HttpClient()
		self._event_bus: EventBus = event_bus
		self._cache: Cache = Cache()

		self.port: int = port
	
	async def Variables(self) -> None:
		"""
		Fetch current playback session from MPC variables endpoint.
		"""

		response: str = await self._client.get(
			f"http://localhost:{self.port}/variables.html"
		)

		p_data: dict = Regex.Variables(response)
		p_session: PlaybackSession = PlaybackSession(p_data)
		p_file: PlaybackFile = PlaybackFile(p_data)

		c_session: PlaybackSession | None = self._cache.get("c_session")
		c_session_ts: float | None = self._cache.get("c_session_ts")
		c_file: PlaybackFile | None = self._cache.get("c_file")

		# Checks if there is a previous session cached.
		c_session_exists = (
			c_session is not None
		)

		# Determines whether a seek occurred by comparing the actual playback
		# position against the expected position based on real elapsed time.
		# A deviation above 3000 (thresold below MPC-HC's 5s seek step)
		# indicates a seek; backward movement is always treated as one.
		p_pos_seeked = (
			c_session is not None
			and c_session_ts is not None
			and p_session.state == PlaybackState.PLAYING
			and (
				p_session.pos < c_session.pos
				# This formula returns the position the player should be at if playing normally.
				or abs(p_session.pos - (c_session.pos + (time.monotonic() - c_session_ts) * 1000)) > 3000
			)
		)

		# Checks if the state of the session
		# (playing/paused/empty) has changed.
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
			
			# cached session timestamp, needed for the seek calculation.
			self._cache.put("c_session_ts", time.monotonic())
			self._cache.put("c_session", p_session)

			return await self._event_bus.publish(
				PlaybackSessionUpdated(p_session)
			)

		# checks if a cached PlaybackFile exists,
		# if it exists, check if the current
		# is equal to the cached one,
		# then update cache and publish event.
		if not c_file or c_file.name != p_file.name:

			self._cache.put("c_file", p_file)

			return await self._event_bus.publish(
				PlaybackFileUpdated(p_file)
			)