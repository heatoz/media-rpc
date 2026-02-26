class Movie:
	"""
	Media Service data model representing a Movie.
	"""

	def __init__(self, title: str, director: str, year: int, poster: str) -> None:
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

		self.director: str = director
		self.poster: str = poster
		self.title: str = title
		self.year: int = year

class Series:
	"""
	Media Service data model representing a Series.
	"""

	def __init__(self, title: str, episode: str, season: str, poster: str) -> None:
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
		"""

		self.episode: int = int(episode)
		self.season: int = int(season)
		self.poster: str = poster
		self.title: str = title