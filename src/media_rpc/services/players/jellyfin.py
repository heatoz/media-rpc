from media_rpc.core.events import PlaybackSessionUpdated, PlaybackFileUpdated
from media_rpc.core.models import PlaybackSession, PlaybackState
from media_rpc.infra import HttpClient, EventBus
from media_rpc.utils import Cache

import time
import json


class Jellyfin:
    """
    Client interface for interacting with a Jellyfin HTTP instance.
    """

    def __init__(
        self,
        event_bus: EventBus,
        token: str, 
        user_name: str,
        host: str = "localhost",
        port: int = 8096,
    ) -> None:
        """
        Initialize the Jellyfin client.

        Args:
            event_bus (EventBus):
                The Event Bus used by the service.

            host (str):
                Hostname or IP of the Jellyfin server.

            token (str):
                API token for authentication.

            user_name (str):
                ID of the user to monitor.

            port (int):
                Port where the Jellyfin server is running.
        """

        self.user_name: str = user_name
        self.host: str = host
        self.port: int = port

        self._event_bus: EventBus = event_bus
        self._cache: Cache = Cache()

        self._client: HttpClient = HttpClient(
            headers={"Authorization": f'MediaBrowser Token="{token}"'}
        )

    async def Sessions(self) -> None:
        """
        Fetches current playback session from Jellyfin sessions endpoint.
        """

        response: dict = json.loads(await self._client.get(
            f"http://{self.host}:{self.port}/Sessions"
        ))

        # fetches the active session of the desired user
        user_session: dict | None = next(
            (
                s
                for s in response
                if s.get("UserName") == self.user_name and s.get("NowPlayingItem")
            ),
            None,
        )

        p_session: PlaybackSession = self._build_session(user_session)

        c_session: PlaybackSession | None = self._cache.get("c_session")
        c_session_ts: float | None = self._cache.get("c_session_ts")

        # Checks if there is a previous session cached.
        c_session_exists = c_session is not None

        # Determines whether a seek occurred by comparing the actual playback
        # position against the expected position based on real elapsed time.
        # A deviation above 3000 (thresold below 5s seek step)
        # indicates a seek; backward movement is always treated as one.
        p_pos_seeked = (
            c_session is not None
            and c_session_ts is not None
            and p_session.state == PlaybackState.PLAYING
            and (
                p_session.pos < c_session.pos
                # This formula returns the position the player should be at if playing normally.
                or abs(
                    p_session.pos
                    - (c_session.pos + (time.monotonic() - c_session_ts) * 1000)
                )
                > 3000
            )
        )

        # Checks if the state of the session
        # (playing/paused/empty) has changed.
        p_state_changed = c_session is not None and (c_session.state != p_session.state)

        # If there is no previous cached session, or
        # the playback position got seeked, or
        # the session state has changed,
        # then update cache and publish event.
        if not c_session_exists or p_pos_seeked or p_state_changed:
            # cached session timestamp, needed for the seek calculation.
            self._cache.put("c_session_ts", time.monotonic())
            self._cache.put("c_session", p_session)

            if p_session.state == PlaybackState.EMPTY:
                self._cache.put("c_session", None)

            await self._event_bus.publish(PlaybackSessionUpdated(p_session))

        # If there is no previous cached file, or
        # the current file name differs from the cached one,
        # then update cache and publish event.
        if p_session.state != PlaybackState.EMPTY and (
            not c_session or c_session.file_name != p_session.file_name
        ):
            self._cache.put("c_session", p_session)
            
            await self._event_bus.publish(PlaybackFileUpdated(p_session.file_name))

    def _build_session(self, session: dict | None) -> PlaybackSession:
        """
        Builds a PlaybackSession from raw Jellyfin Sessions endpoint data.

        Args:
            session (dict, None):
                Jellyfin /Sessions raw response data.

        Returns:
            PlaybackSession:
                A parsed PlaybackSession object.
        """

        if not session or not session.get("NowPlayingItem"):
            return PlaybackSession(
                state = PlaybackState.EMPTY,
                pos = 0,
                dur = 0,
                file_name = ""
            )

        play_state = session.get("PlayState", {})
        item = session["NowPlayingItem"]

        is_paused: bool = play_state.get("IsPaused", False)

        # Jellyfin returns position on ticks, convert it to miliseconds
        # to keep it supported by the RPC service.
        pos_ticks: int = play_state.get("PositionTicks", 0)
        dur_ticks: int = session["NowPlayingItem"].get("RunTimeTicks", 0)

        return PlaybackSession(
            state = PlaybackState.PAUSED if is_paused else PlaybackState.PLAYING,
            pos = pos_ticks // 10_000,
            dur = dur_ticks // 10_000,
            file_name = item.get("Path")
        )
