from mpcrpc.utils import Regex, Filename
from mpcrpc.infra import HttpClient
from typing import Dict
import asyncio
import pytest

# Didn't do a class for Filename since
# it's just a wrapper of guessit

async def GetVariables(port: int) -> str:
    """
    Fetches the raw variables HTML from a running MPC-HC HTTP interface.

    Args:
        port (int): The port number where MPC-HC HTTP server is running.

    Returns:
        str: The raw HTML content returned by the HTTP server.

    Raises:
        aiohttp.ClientError: If the HTTP request fails.
    """
    http_client: HttpClient = HttpClient()
    response: str = await http_client.get(f"http://localhost:{port}/variables.html")
    return response

class TestRegex:
    """
    Unit tests for the Regex parsing logic class.

    Tests the parsing of raw MPC-HC variables HTML into a dictionary.
    """

    @pytest.mark.asyncio
    async def test_response_dict(self) -> None:
        """
        Ensure that Regex.Variables() returns a dictionary
        with 5 keys, all values must be non-empty strings.

        Raises:
            AssertionError: If the dictionary does not meet expected conditions.
        """

        response: str = await GetVariables(13579)
        result: dict[str, str] = Regex.Variables(response)

        # Check number of keys
        assert len(result) == 5, f"Expected 5 keys, got {len(result)}"

        # Check all values are non-empty strings
        for key, value in result.items():
            assert isinstance(value, str), f"Value for key '{key}' is not a string"
            assert value.strip() != "", f"Value for key '{key}' is empty"