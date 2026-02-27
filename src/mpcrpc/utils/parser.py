from guessit import guessit
import re

class Filename:
	"""
	Represents a parsed media file.
	"""

	def __init__(self) -> None:
		"""
		Thin wrapper around guessit.
		
		Args:
			filename (str):
				Filename.
				
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

	def Parse(self, filename: str) -> None:
		"""
		Parses a raw file name into a parsed object.

		Args:
			filename (str):
				The file to be parsed filename.
		"""

		# sadly couldn't type annotate this :(
		matches = guessit(filename)

		for key, value in matches.items():
			setattr(self, key, value)

class Regex:
	"""
	Contains all regex data parsing logic.

	Created so the MPC service models do not need
	to be concerned with regex details.
	"""

	# MPC /variables endpoint P matcher
	P_TAG: re.Pattern = re.compile(
		r'<p id="(file|filedir|state|position|duration)">(.+?)</p>',
		re.IGNORECASE
	)

	@staticmethod
	def Variables(raw: str) -> dict[str, str]:
		"""
		Parses the raw HTML returned by the Variables endpoint.

		Args:
			raw (str):
				The raw HTML content.

		Returns:
			dict:
				A dictionary containing the parsed data.
		"""

		return dict(Regex.P_TAG.findall(raw))