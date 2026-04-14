from mpcrpc.infra import HttpClient


class Litterbox:
    """
    Adapter for the Litterbox (catbox.moe) service.
    """

    def __init__(self) -> None:
        """
        Initialize a Litterbox uploader object.
        """

        self._client: HttpClient = HttpClient()

    async def Upload(self, image: bytes) -> str:
        """
        Uploads an image on Litterbox.

        Args:
            image (bytes):
                The image to be uploaded in bytes.
            filename (str):
                The filename for the uploaded image.

        Returns:
            str:
                The image url.
        """

        response: str = await self._client.post(
            "https://litterbox.catbox.moe/resources/internals/api.php",
            data={
                "reqtype": "fileupload",
                "time": "12h",
                "fileToUpload": image,
            },
        )

        return response