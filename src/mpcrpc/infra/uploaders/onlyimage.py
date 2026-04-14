from mpcrpc.infra import HttpClient
import base64
import json


class OnlyImage:
    """
    Adapter for the OnlyImage service.
    """

    def __init__(self, api_key: str) -> None:
        self._client: HttpClient = HttpClient(headers={"X-API-Key": api_key})

    async def Upload(self, image: bytes) -> str:
        """
        Uploads an image on OnlyImage.

        Args:
            image (bytes):
                The image to be uploaded in bytes.

        Returns:
            str:
                The image url.
        """

        image_b64 = base64.b64encode(image).decode("utf-8")

        response = await self._client.post(
            "https://onlyimage.org/api/1/upload",
            data={"source": image_b64, "expiration": "PT12H"},
        )

        return json.loads(response)["image"]["url"]
