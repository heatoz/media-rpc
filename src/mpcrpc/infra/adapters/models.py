class SearchResult:
    """
    Represents the result of a Search operation.
    """

    def __init__(self, id: str, type: str) -> None:
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

    def __init__(self, director: str, poster: str, title: str, year: str) -> None:
        """
        Initialize a QueryResult object.

        Attributes:
            director (str):
                The media director.

            poster (str):
                The media poster url.

            title (str):
                The media title.

            year (str):
                The media release year.
        """

        self.director: str = director
        self.poster: str = poster
        self.title: str = title
        self.year: str = year
