from mpcrpc.infra.adapters import QueryResult, IMDB, TMDB

from mpcrpc.core.events import PlaybackFileUpdated, MediaParsed

from mpcrpc.core.models import Movie, Series

from mpcrpc.utils import MediaFile
from mpcrpc.infra import EventBus


class Media:
    """
    Media Service created to parse a Movie / Series object
    out of the MPC-HC Web Interface /variables "file" field.
    """

    def __init__(self, event_bus: EventBus, adapter: IMDB | TMDB):
        """
        Initialize a Media Service object.

        Args:
                event_bus (EventBus):
                        The Event Bus used by the service.

                adapter (IMDB | TMDB):
                        The adapter used to get the metadata.
                        It should be initialized and configured by
                        the entry point.
        """

        self._event_bus: EventBus = event_bus

        # Subscribes Parse() to PlaybackFileUpdated.
        self._event_bus.subscribe(PlaybackFileUpdated, self.Parse)

        self.adapter: IMDB | TMDB = adapter

    async def Parse(self, event: PlaybackFileUpdated) -> None:
        """
        Parses a PlaybackFile received from PlaybackFileUpdated
        event and publishes the parsed media data to the event bus.

        This function handles both movies and series. It uses the adapter
        to search for metadata and safely extracts attributes from the
        playback file to avoid errors.

        Note:
                If the PlaybackFile is not recognized by the adapter,
                in other words, if the search returns nothing, the
                MediaParsed event is not going to be sent, resulting
                on the RPC Service not updating Rich Presence.
                Also, depending on the filename, wrong presences
                could be presented. I don't think there's a solution
                to that, please rename your files.

        Args:
                event (PlaybackFileUpdated):
                        The PlaybackFileUpdated event, contains
                        the PlaybackFile as p_file, which contains
                        the filename on name attribute.
        """

        # Note: named the parsed mediafile to m_file
        # to avoid confusions with the raw playbackfile p_file.
        m_file: MediaFile = MediaFile.Parse(event.p_file.name)

        # Returns None if search finds nothing.
        query_r: QueryResult | None = await self.adapter.Fetch(m_file)

        if query_r:

            # decided to check types using the m_file
            # because it ensures we'll not fall for
            # the adapter wrong search results.
            if m_file.type == "episode":
                # Safely get episode and season attributes from the
                # playback file since that's the only way to get them.
                # If they don't exist, default to None to avoid AttributeError.
                await self._event_bus.publish(
                    MediaParsed(
                        Series(
                            title=query_r.title,
                            episode=getattr(m_file, "episode", None),
                            season=getattr(m_file, "season", None),
                            poster=query_r.poster,
                            episode_title=query_r.episode_title,
                        )
                    )
                )

            if m_file.type == "movie":
                await self._event_bus.publish(
                    MediaParsed(
                        Movie(
                            title=query_r.title,
                            director=query_r.director,
                            year=query_r.year,
                            poster=query_r.poster,
                        )
                    )
                )
