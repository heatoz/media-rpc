from mpcrpc.infra import HttpClient
from aiohttp import FormData

class Litterbox:
    """
    Adapter for the Litterbox (catbox.moe) service.
    """

    def __init__(self) -> None:
        self._client: HttpClient = HttpClient()

    async def Upload(self, image: bytes) -> str:
        """
        Uploads an image on Litterbox.

        Args:
            image (bytes):
                The image to be uploaded in bytes.

        Returns:
            str:
                The image url.
        """

        form = FormData()
        form.add_field("reqtype", "fileupload")
        form.add_field("time", "12h")
        form.add_field("fileToUpload", image)

        response: str = await self._client.post(
            "https://litterbox.catbox.moe/resources/internals/api.php",
            data=form,
        )

        return response