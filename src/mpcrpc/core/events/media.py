from mpcrpc.core.models import Movie, Series

class MediaParsed:
    """
    Triggered when Media Service finishes parsing.
    """

    def __init__(self, media: Movie | Series):
        """
        Initialize a MediaParsed object.

        Args:
            media (Movie | Series):
                The parsed media.
        """
        
        self.media = media