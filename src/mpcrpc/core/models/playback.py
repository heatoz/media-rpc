from enum import IntEnum


class PlaybackSession:
    """
    Represents an MPC playback session.
    """

    def __init__(self, file_name: str, state: int, pos: int, dur: int) -> None:
        """
        Initializes a PlaybackSession instance.

        Args:
                p_data (dict):
                        A dictionary containing parsed data from the Variables endpoint.
                        This dictionary should be the return value of Parser.Variables().

        Raises:
                KeyError:
                        If any required playback fields are missing.
        """

        self.file_name: str = file_name
        self.state: int = state
        self.pos: int = pos
        self.dur: int = dur

class PlaybackState(IntEnum):
    """
    Enum representing the MPC-HC Web Interface
    PlaybackSession states, created for better
    management on RPC Service.
    """

    PLAYING = 2
    PAUSED = 1
    EMPTY = -1
