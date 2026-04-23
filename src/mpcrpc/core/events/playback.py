from mpcrpc.core.models import PlaybackSession


class PlaybackSessionUpdated:
    """
    Represents a PlaybackSession update triggered by the MPC poller service.
    """

    def __init__(self, p_session: PlaybackSession) -> None:
        """
        Initializes a PlaybackSessionUpdated event type.

        Attributes:
            p_session (PlaybackSession):
                The updated PlaybackSession.
        """

        self.p_session: PlaybackSession = p_session


class PlaybackFileUpdated:
    """
    Represents a PlaybackFile update triggered by the MPC poller service.
    """

    def __init__(self, file_name: str) -> None:
        """
        Initializes a PlaybackFileUpdated event type.

        Attributes:
            p_file (PlaybackFile):
                The updated PlaybackFile.
        """

        self.file_name: str = file_name
