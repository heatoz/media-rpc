import re

# MPC /variables endpoint P matcher
P_TAG: re.Pattern = re.compile(
	r'<p id="(file|filedir|state|position|duration)">(.+?)</p>',
	re.IGNORECASE
)

class Parser:
	"""
	Contains all regex data parsing logic.

	Created so the MPC service models do not need
	to be concerned with regex details.
	"""

	@staticmethod
	def Variables(raw: str) -> dict:
		"""
		Parses the raw HTML returned by the Variables endpoint.

		Args:
			raw (str):
				The raw HTML content.

		Returns:
			dict:
				A dictionary containing the parsed data.
		"""

		return dict(P_TAG.findall(raw))