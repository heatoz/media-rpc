from media_rpc.core.events import PlaybackSessionUpdated, PlaybackFileUpdated
from media_rpc.core.models import PlaybackSession, PlaybackState
from media_rpc.infra import HttpClient, EventBus
from media_rpc.utils import Cache

import xml.etree.ElementTree as ET
import base64
import time


class VLC:
    """
    Client interface for interacting with a VLC HTTP instance.
    """

    def __init__(
        self,
        event_bus: EventBus,
        password: str,
        host: str = "localhost",
        port: int = 8080,
    ) -> None:
        """
        Initialize the VLC client.

        Args:
            event_bus (EventBus):
                The Event Bus used by the service.

            password (str):
                Password for VLC's HTTP interface authentication.

            host (str):
                Hostname or IP of the VLC HTTP interface.

            port (int):
                Port where the VLC HTTP interface is running.
        """

        credentials = base64.b64encode(f":{password}".encode()).decode()
        self._client: HttpClient = HttpClient(
            headers={"Authorization": f"Basic {credentials}"}
        )

        self._event_bus: EventBus = event_bus
        self._cache: Cache = Cache()

        self.host: str = host
        self.port: int = port

    async def Status(self) -> None:
        """
        Fetches current playback session from VLC status endpoint.
        """

        response: str = await self._client.get(
            f"http://{self.host}:{self.port}/requests/status.xml"
        )

        p_session: PlaybackSession = self._build_session(response)

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

    def _build_session(self, response: str) -> PlaybackSession:
        """
        Builds a PlaybackSession from raw VLC status XML data.

        Args:
            response (str):
                VLC /requests/status.xml raw response body.

        Returns:
            PlaybackSession:
                A parsed PlaybackSession object.
        """

        try:
            root = ET.fromstring(response)
        except ET.ParseError:
            return PlaybackSession(
                state=PlaybackState.EMPTY,
                pos=0,
                dur=0,
                file_name=""
            )

        state_text = root.findtext("state", default="stopped")

        if state_text == "stopped":
            return PlaybackSession(
                state=PlaybackState.EMPTY,
                pos=0,
                dur=0,
                file_name=""
            )

        # VLC returns position in seconds and length in seconds
        pos_sec: int = int(root.findtext("time", default="0"))
        dur_sec: int = int(root.findtext("length", default="0"))

        # Extract filename from meta category
        file_name: str = ""
        for category in root.findall("information/category"):
            if category.get("name") == "meta":
                for info in category.findall("info"):
                    if info.get("name") == "filename":
                        file_name = info.text or ""
                        break

        return PlaybackSession(
            state=PlaybackState.PAUSED if state_text == "paused" else PlaybackState.PLAYING,
            pos=pos_sec * 1000,
            dur=dur_sec * 1000,
            file_name=file_name
        )