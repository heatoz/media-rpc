class Movie:
    """
    Media Service data model representing a Movie.
    """

    def __init__(self, title: str, director: str, year: int | str, poster: str) -> None:
        """
        Initialize a Movie data object.

        Attributes:
                title (str):
                        The Movie title.

                director (str):
                        The Movie director.

                year (int):
                        The Movie release year.

                poster (str):
                        A url containing the movie poster.
        """

        self.year: int = int(year)
        self.director: str = director
        self.poster: str = poster
        self.title: str = title


class Series:
    """
    Media Service data model representing a Series.
    """

    def __init__(
        self,
        title: str,
        episode: str,
        season: str,
        poster: str,
        episode_title: str = None,
    ) -> None:
        """
        Initialize a Series data object.

        Attributes:
                title (str):
                        The Series title.

                episode (int):
                        The Series episode.

                season (int):
                        The Series season.

                poster (str):
                        A url containing the series season poster.

                episode_title (str, optional):
                        The Series episode title.
        """

        self.episode: int = int(episode)
        self.season: int = int(season)
        self.poster: str = poster
        self.title: str = title
        self.episode_title: str | None = episode_title
