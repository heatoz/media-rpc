from mpcrpc.core.events import PlaybackFileUpdated, PlaybackSessionUpdated, MediaParsed

from mpcrpc.core.models import PlaybackSession, PlaybackState, Movie, Series

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

        # Subscribes HandleFileUpdated()
        # to PlaybackFileUpdated.
        self._event_bus.subscribe(PlaybackFileUpdated, self.HandleFileUpdated)

        # Subscribes HandleSessionUpdated()
        # to PlaybackSessionUpdated.
        self._event_bus.subscribe(PlaybackSessionUpdated, self.HandleSessionUpdated)

        # Subscribes HandleMediaParsed()
        # to MediaParsed.
        self._event_bus.subscribe(MediaParsed, self.HandleMediaParsed)

    async def start(self, client_id: int) -> None:
        """
        Initialize a new AioPresence object.

        Args:
                        client_id (int):
                                        Client id to start the presence on.

        Note:
                        I know a separated method just for
                        that isn't very good, but the connect
                        method had to be awaited.
        """

        self._rpc: AioPresence = AioPresence(client_id)

        await self._rpc.connect()

    async def HandleFileUpdated(self, event: PlaybackFileUpdated) -> None:
        """
        PlaybackFileUpdated event handler.

        Note:
                        The only reason this handler is here is to
                        avoid stale presences when switching from a
                        recognized media to one that isn't recognized,
                        avoiding that only PlaybackSession gets updated.

        Args:
                        event (PlaybackFileUpdated):
                                        The PlaybackFileUpdated event, contains
                                        the PlaybackFile as p_file.
        """

        if self._cache.get("c_media"):
            self._cache.put("c_media", None)

            await self._rpc.clear()

    async def HandleSessionUpdated(self, event: PlaybackSessionUpdated) -> None:
        """
        PlaybackSessionUpdated event handler.

        Args:
                        event (PlaybackSessionUpdated):
                                        The PlaybackSessionUpdated event, contains
                                        the PlaybackSession as p_session.
        """

        c_media: Movie | Series | None = self._cache.get("c_media")

        p_session: PlaybackSession = event.p_session

        self._cache.put("c_session", p_session)

        # Check if there is a Media already cached and
        # being presented at the rich presence, only
        # updates the presence if there is.
        # Made to avoid sending faulty presence
        # on the first events.
        if c_media:
            await self.Update(p_session, c_media)

        else:
            # c_session pending since, implemented to calculate
            # the delay time on first events when sessionupdated
            # comes first, and since there isn't really a mediaparsed
            # it takes a little time to get into the rpc, this fixes
            # that.
            self._cache.put("c_session_ps", time.time())

    async def HandleMediaParsed(self, event: MediaParsed) -> None:
        """
        MediaParsed event handler.

        Args:
                        event (MediaParsed):
                                        The MediaParsed event, contains
                                        the Media as media.
        """

        c_session: PlaybackSession | None = self._cache.get("c_session")
        c_session_ps: float | None = self._cache.get("c_session_ps")

        media: Movie | Series = event.media

        self._cache.put("c_media", media)

        # Check if there is a Session already cached and
        # being presented at the rich presence, only
        # updates the presence if there is.
        # Made to avoid sending faulty presence
        # on the first events.
        if c_session:
            # checks if c_session was pending for this mediaparsed.
            if c_session_ps:
                delay_ms = int((time.time() - c_session_ps) * 1000)
                c_session.pos += delay_ms

                # reset c_session pending since because
                # the delay is already fixed.
                self._cache.put("c_session_ps", None)

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
            self._cache.put("c_session", None)
            self._cache.put("c_media", None)

            await self._rpc.clear()

        if isinstance(media, Movie):
            if p_session.state == PlaybackState.PAUSED:
                await self._rpc.update(
                    activity_type=ActivityType.WATCHING,
                    name=media.title,
                    state=f"{media.director} ({media.year})",
                    large_image=media.poster,
                    small_image="https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/paused.png",
                    small_text="Paused",
                )

            if p_session.state == PlaybackState.PLAYING:
                now: int = int(time.mktime(time.localtime()))
                start: int = now - p_session.pos // 1000
                end: int = now + (p_session.dur - p_session.pos) // 1000

                await self._rpc.update(
                    activity_type=ActivityType.WATCHING,
                    start=start,
                    end=end,
                    name=media.title,
                    state=f"{media.director} ({media.year})",
                    large_image=media.poster,
                )

        if isinstance(media, Series):
            # pretty ugly implementation, i'll change that on future
            parts = []

            if media.episode:
                parts.append(f"Episode {media.episode}")
            if media.season:
                parts.append(f"Season {media.season}")

            state = " • ".join(parts) if parts else None

            if p_session.state == PlaybackState.PAUSED:
                await self._rpc.update(
                    activity_type=ActivityType.WATCHING,
                    name=media.title,
                    state=state,
                    large_image=media.poster,
                    small_image="https://raw.githubusercontent.com/heatoz/mpc-rpc/refs/heads/master/assets/paused.png",
                    small_text="Paused",
                    details=media.episode_title,
                )

            if p_session.state == PlaybackState.PLAYING:
                now: int = int(time.mktime(time.localtime()))
                start: int = now - p_session.pos // 1000
                end: int = now + (p_session.dur - p_session.pos) // 1000

                await self._rpc.update(
                    activity_type=ActivityType.WATCHING,
                    start=start,
                    end=end,
                    name=media.title,
                    state=state,
                    large_image=media.poster,
                    details=media.episode_title,
                )
