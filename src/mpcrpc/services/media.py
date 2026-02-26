from mpcrpc.core.events import PlaybackFileUpdated, MediaParsed
from mpcrpc.core.models import PlaybackFile, Movie, Series
from mpcrpc.infra.adapters import IMDB, TMDB
from mpcrpc.infra import EventBus
from mpcrpc.utils import Filename

class Media:
	"""
	Media Service created to parse a Movie / Series object
	out of the MPC-HC Web Interface /variables "file" field.
	"""

	def __init__(
		self,
		event_bus: EventBus,
		adapter: IMDB | TMDB
	):
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
		self._event_bus.subscribe(
			PlaybackFileUpdated,
			self.Parse
		)

		self.adapter: IMDB | TMDB = adapter

	async def Parse(self, p_file: PlaybackFile) -> None:
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
			p_file (PlaybackFile):
				The PlaybackFile from PlaybackFileUpdated.
		"""

		p_file: Filename = Filename(p_file.title)

		# Returns a id that follows the adapter format,
		# for example: tt0308664 for IMDB, 1398 for TMDB.
		search_r: str = await self.adapter.Search(p_file.title)

		if search_r:

			# Makes a detailed query using the id returned
			# by the search. Made the Media type checks
			# use this value instead of the p_file because
			# sometimes guessit does a wrong match.
			query_r: dict[str, str | int] = await self.adapter.Query(search_r)

			if query_r["type"] == "series":

				# Safely get episode and season attributes from the
				# playback file since that's the only way to get them.
            	# If they don't exist, default to None to avoid AttributeError.
				# TODO: Make TVDB query for the episode title.
				self._event_bus.publish(
					MediaParsed(
						Series(
							title = query_r["title"],
							# A Series MUST have a Season and Episode
							# I've thought about making it optional
							# because of some guessit mismatch cases
							# but haven't had the time for that.
							episode = p_file["episode"],
							season = p_file["season"],
							poster = query_r["poster"]
						)
					)
				)

			if query_r["type"] == "movie":

				self._event_bus.publish(
					MediaParsed(
						Movie(
							title = query_r["title"],
							director = query_r["director"],
							year = query_r["year"],
							poster = query_r["poster"]
						)
					)
				)
