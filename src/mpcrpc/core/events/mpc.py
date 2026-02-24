from mpcrpc.core.models import PlaybackSession

class PlaybackSessionUpdated:
    """
    Represents a PlaybackSession update triggered by MPC service.
    """

    def __init__(self, p_session: PlaybackSession) -> None:
        """
        Initializes a PlaybackSessionUpdated event type.

        Attributes:
            p_session (PlaybackSession):
                The updated PlaybackSession.
        """

        self.p_session: PlaybackSession = p_session