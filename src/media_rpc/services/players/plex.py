from media_rpc.core.events import PlaybackSessionUpdated, PlaybackFileUpdated
from media_rpc.core.models import PlaybackSession, PlaybackState
from media_rpc.infra import HttpClient, EventBus
from media_rpc.utils import Cache

import time
import json


class Plex:
    """
    Client interface for interacting with a Plex HTTP instance.
    """

    def __init__(
        self,
        event_bus: EventBus,
        token: str,
        user_name: str,
        host: str = "localhost",
        port: int = 32400,
    ) -> None:
        """
        Initialize the Plex client.

        Args:
            event_bus (EventBus):
                The Event Bus used by the service.

            host (str):
                Hostname or IP of the Plex server.

            token (str):
                X-Plex-Token for authentication.

            user_name (str):
                Username to monitor.

            port (int):
                Port where the Plex server is running.
        """

        self.user_name: str = user_name
        self.host: str = host
        self.port: int = port

        self._event_bus: EventBus = event_bus
        self._cache: Cache = Cache()

        self._client: HttpClient = HttpClient(
            headers={
                "X-Plex-Token": token,
                "Accept": "application/json",
            }
        )

    async def Sessions(self) -> None:
        """
        Fetches current playback session from Plex sessions endpoint.
        """

        response: dict = json.loads(await self._client.get(
            f"http://{self.host}:{self.port}/status/sessions"
        ))

        sessions: list = response.get("MediaContainer", {}).get("Metadata", [])

        # Fetches the active session of the desired user
        user_session: dict | None = next(
            (
                s
                for s in sessions
                if s.get("User", {}).get("title") == self.user_name
            ),
            None,
        )

        p_session: PlaybackSession = await self._build_session(user_session)

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
                > 8000
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
    
    async def _build_session(self, session: dict | None) -> PlaybackSession:
        """
        Builds a PlaybackSession from raw Plex Sessions endpoint data.

        Args:
            session (dict, None):
                Plex /status/sessions raw response data.

        Returns:
            PlaybackSession:
                A parsed PlaybackSession object.
        """

        if not session:
            return PlaybackSession(
                file_name="",
                state=PlaybackState.EMPTY,
                pos=0,
                dur=0
            )

        player: dict = session.get("Player", {})
        is_paused: bool = player.get("state") == "paused"

        rating_key: str = session.get("ratingKey", "")
        
        file_path: str = ""
        
        # avoid requesting the rating_key again
        # if it was already requested.
        if rating_key:
            c_path = self._cache.get(rating_key)

            if c_path:
                file_path = c_path
            else:
                file_path = await self._fetch_file_path(rating_key)

                self._cache.put(rating_key, file_path)
        
        return PlaybackSession(
            file_name=file_path,
            state=PlaybackState.PAUSED if is_paused else PlaybackState.PLAYING,
            pos=int(session.get("viewOffset", 0)),
            dur=int(session.get("duration", 0)),
        )

    async def _fetch_file_path(self, rating_key: str) -> str:
        """
        Fetches the actual file path from the library metadata endpoint.

        Args:
            rating_key (str):
                Rating Key used to poll the file path/name.
            
        Returns:
            str:
                The full file path (contains the file name).
        """

        response: dict = json.loads(await self._client.get(
            f"http://{self.host}:{self.port}/library/metadata/{rating_key}"
        ))

        return (
            response.get("MediaContainer", {})
            .get("Metadata", [{}])[0]
            .get("Media", [{}])[0]
            .get("Part", [{}])[0]
            .get("file", "")
        )