class PlaybackSession:
	"""
	Represents an MPC playback session.
	"""

	def __init__(self, p_data: dict) -> None:
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

		self.state: str = p_data["state"]
		self.pos: str = p_data["position"]
		self.dur: str = p_data["duration"]

class PlaybackFile:
	"""
	Represents an MPC playback file.
	"""

	def __init__(self, p_data: dict) -> None:
		"""
		Initializes a PlaybackFile instance.

		Args:
			p_data (dict):
				A dictionary containing parsed data from the Variables endpoint.
				This dictionary should be the return value of Parser.Variables().

		Raises:
			KeyError:
				If any required playback fields are missing.
		"""

		self.name: str = p_data["file"]