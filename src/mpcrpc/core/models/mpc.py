import re

# MPC /variables P tags pattern
P_TAG: re.Pattern = re.compile(
	r'<p id="(file|filedir|state|position|duration)">(.+?)</p>',
	re.IGNORECASE
)

class PlaybackSession:
	"""
	Represents a MPC Playback Session.
	"""

	def __init__(self, raw: str) -> None:
		"""
		Initialize a PlaybackSession from raw MPC HTML response.

		Args:
			raw (str):
				HTML string returned by the MPC variables endpoint.

		Raises:
			KeyError:
				If required playback fields are missing.
		"""
		match: dict = dict(P_TAG.findall(raw))

		self.file: str = match["file"]
		self.state: str = match["state"]
		self.pos: str = match["position"]
		self.dur: str = match["duration"]