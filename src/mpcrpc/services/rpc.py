from mpcrpc.core.models import PlaybackSession, PlaybackState, Movie, Series
from mpcrpc.core.events import PlaybackSessionUpdated, MediaParsed
from pypresence.types import ActivityType
from pypresence import AioPresence
from mpcrpc.infra import EventBus
from mpcrpc.utils import Cache
import time

class RPC:
	"""
	Manages the Discord Rich Presence operations.
	"""

	def __init__(self, event_bus: EventBus) -> None:
		"""
		Initialize a RPC Service object.

		Attributes:
			cache (Cache):
				The service cache manager.

			event_bus (EventBus):
				The EventBus used by the service.
			
			rpc (AioPresence):
				The Discord rich presence manager.
		"""

		self._cache: Cache = Cache()

		self._event_bus: EventBus = event_bus

		# Subscribes HandleSessionUpdated()
		# to PlaybackSessionUpdated.
		self._event_bus.subscribe(
			PlaybackSessionUpdated,
			self.HandleSessionUpdated
		)

		# Subscribes HandleMediaParsed()
		# to MediaParsed.
		self._event_bus.subscribe(
			MediaParsed,
			self.HandleMediaParsed
		)

	async def start(self) -> None:
		"""
		Initialize a new AioPresence object.

		Note:
			I know a separated method just for
			that isn't very good, but the connect
			method had to be awaited.
		"""

		# mpc-rpc discord application id.
		self._rpc: AioPresence = AioPresence(1411516401541185566)

		await self._rpc.connect()

	async def HandleSessionUpdated(self, event: PlaybackSessionUpdated) -> None:
		"""
			PlaybackSessionUpdated event handler.

			Args:
				event (PlaybackSessionUpdated):
					The PlaybackSessionUpdated event, contains
					the PlaybackSession as p_session.
		"""

		p_session: PlaybackSession = event.p_session

		self._cache.put("c_session", p_session)

		c_media: Movie | Series | None = self._cache.get("c_media")

		# Check if there is a Media already cached and
		# being presented at the rich presence, only
		# updates the presence if there is.
		# Made to avoid sending faulty presence
		# on the first events.
		if c_media:
			
			await self.Update(p_session.p_session, c_media)
			

	async def HandleMediaParsed(self, event: MediaParsed) -> None:
		"""
			MediaParsed event handler.

			Args:
				event (MediaParsed):
					The MediaParsed event, contains
					the Media as media.
		"""

		media: Movie | Series = event.media

		self._cache.put("c_media", media)

		c_session: PlaybackSession | None = self._cache.get("c_session")

		# Check if there is a Session already cached and
		# being presented at the rich presence, only
		# updates the presence if there is.
		# Made to avoid sending faulty presence
		# on the first events.
		if c_session:
			
			await self.Update(c_session, media)

	async def Update(self, p_session: PlaybackSession, media: Movie | Series) -> None:
		"""
		Updates Discord rich presence.

		Note:
			I know this function is quite a mess due
			to all these if conditions, but i didn't
			find a solution to it so, it's staying there :)

		Args:
			p_session (PlaybackSession):
				PlaybackSession to be updated.
			
			media (Movie | Series):
				Media to be updated.
		"""

		if p_session.state == PlaybackState.EMPTY:
			
			await self._rpc.clear()

		if p_session.state == PlaybackState.PAUSED:

			if isinstance(media, Movie):
				await self._rpc.update(
					activity_type = ActivityType.WATCHING,
					name = media.title,
					state = f"{media.director}, {media.year}",
					large_image = media.poster,
					small_image = "https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/paused.png",
					small_text = "Paused"
				)

			if isinstance(media, Series):
				await self._rpc.update(
					activity_type = ActivityType.WATCHING,
					name = media.title,
					state = f"Episode {media.episode}, Season {media.season}",
					large_image = media.poster,
					small_image = "https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/paused.png",
					small_text = "Paused"
				)        

		if p_session.state == PlaybackState.PLAYING:

			now: int = int(time.time() * 1000)

			if isinstance(media, Movie):
				await self._rpc.update(
					activity_type = ActivityType.WATCHING,
					start = now - p_session.pos,
					end = now - p_session.pos + p_session.dur,
					name = media.title,
					state = f"{media.director}, {media.year}",
					large_image = media.poster,
					small_image = "https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/playing.png",
					small_text = "Playing"
				)

			if isinstance(media, Series):
				await self._rpc.update(
					activity_type = ActivityType.WATCHING,
					start = now - p_session.pos,
					end = now - p_session.pos + p_session.dur,
					name = media.title,
					state = f"Episode {media.episode}, Season {media.season}",
					large_image = media.poster,
					small_image = "https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/playing.png",
					small_text = "Playing"
				)