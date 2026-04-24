from guessit import guessit


class MediaFile:
    """
    Represents a parsed media file.
    """

    def __init__(self) -> None:
        """
        Thin wrapper around guessit.

        Attributes:
                title (str):
                        Main title of the media.

                type (str):
                        Media type as detected by guessit (e.g., "movie", "episode").

                year (int, optional):
                        Release year of the media.

                season (int, optional):
                        Season number (for episodic content).

                episode (int, optional):
                        Episode number (for episodic content).

                episode_title (str, optional):
                        Title of the episode.

                alternative_title (str, optional):
                        Secondary or alternative title detected in the filename.

                screen_size (str, optional):
                        Video resolution (e.g., "720p", "1080p").

                source (str, optional):
                        Source of the media (e.g., "Web", "HDTV").

                other (str, optional):
                        Additional release information (e.g., "Rip").

                video_codec (str, optional):
                        Video codec used (e.g., "H.264").

                audio_codec (str, optional):
                        Audio codec used (e.g., "AAC").

                audio_channels (str, optional):
                        Audio channel configuration (e.g., "2.0").

                release_group (str, optional):
                        Release group tag.

                container (str):
                        Media container format (e.g., "mkv").

                mimetype (str):
                        MIME type of the container (e.g., "video/x-matroska").
        """

    @staticmethod
    def Parse(filename: str) -> MediaFile:
        """
        Parses a raw file name into a parsed object.

        Args:
                filename (str):
                        The file to be parsed filename.
        """

        m_file: MediaFile = MediaFile()

        # sadly couldn't type annotate this :(
        matches = guessit(filename)

        for key, value in matches.items():
            setattr(m_file, key, value)

        return m_file
