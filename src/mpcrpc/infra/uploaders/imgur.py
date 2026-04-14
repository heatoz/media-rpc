from mpcrpc.infra import HttpClient
import base64

class Imgur:
    """
    Adapter for the Imgur service.
    """

    def __init__(self, token: str) -> None:
        self._client: HttpClient = HttpClient(
            headers={
                "Authorization": f"Client-ID {token}"
            }
        )

    async def Upload(self, image: bytes) -> str:
        """
        Uploads an image on Imgur.

        Args:
            image (bytes):
                The image to be uploaded in bytes.

        Returns:
            str:
                The image url.
        """

        image_b64 = base64.b64encode(image).decode("utf-8")

        response = await self._client.post(
            "https://api.imgur.com/3/image",
            json={
                "image": image_b64,
                "type": "base64",
            }
        )

        return response["data"]["link"]