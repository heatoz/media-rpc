class SearchResult:
    """
    Represents the result of a Search operation.
    """

    def __init__(self, id: str) -> None:
        """
        Initialize a SearchResult object.

        Attributes:

            id (str):
                The id of the media that was
                queried by the search operation.
        """

        self.id: str = id


class QueryResult:
    """
    Represents the result of a Query operation.
    """

    def __init__(
        self,
        poster: str,
        title: str,
        year: str | None = None,
        director: str | None = None,
        episode_title: str | None = None,
    ) -> None:
        """
        Initialize a QueryResult object.

        Attributes:

            poster (str):
                The media poster url.

            title (str):
                The media title.

            year (optional, str):
                The media (movie) release year.

            director (optional, str):
                The media (movie) director.

            episode_title (optional, str):
                The media (series) episode title.
        """

        self.poster: str = poster
        self.title: str = title
        self.year: str | None = year
        self.director: str | None = director
        self.episode_title: str | None = episode_title
