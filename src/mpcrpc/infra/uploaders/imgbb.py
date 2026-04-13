from mpcrpc.infra import HttpClient
import base64
import json

class ImgBB:
    """
    Adapter for the ImgBB service.
    """

    def __init__(self, token: str) -> None:
        """
        Initialize a ImgBB uploader object.

        Args:
            token (str):
                A ImgBB API token.
        """

        self._client: HttpClient = HttpClient()
        self.token: str = token

    async def Upload(self, image: bytes) -> str:
        """
        Uploads a image on ImgBB.

        Args:
            image (bytes):
                The image to be uploaded on bytes.

        Returns:
            str:
                The image url.
        """

        response: str = await self._client.post(
            "https://api.imgbb.com/1/upload",
            data={
                "key": self.token,
                "image": base64.b64encode(image).decode(),
            },
        )

        return json.loads(response).get("data").get("url")
