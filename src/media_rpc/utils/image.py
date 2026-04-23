from media_rpc.infra import HttpClient
from PIL import Image as PImage
import io


class Image:
    """
    Represents a processed image.
    """

    def __init__(self) -> None:
        self._client: HttpClient = HttpClient()

    async def Process(self, url: str) -> bytes:
        """
        Process an image from a URL, fitting it into a 256x256 square.

        Args:
                url (str):
                        The URL of the image to be fetched and processed.

        Returns:
                bytes:
                        Processed image as bytes.

        Raises:
                requests.exceptions.RequestException:
                        If the image cannot be fetched from the given URL.
        """

        img = PImage.open(io.BytesIO(await self._client.get_bytes(url))).convert("RGBA")

        width, height = img.size
        long_length = max(width, height)

        if width != height:
            new_img = PImage.new("RGBA", (long_length, long_length), (0, 0, 0, 0))
            new_img.paste(
                img, ((long_length - width) // 2, (long_length - height) // 2)
            )
            img = new_img
            width = height = long_length

        if long_length > 256:
            ratio = 256 / long_length
            img = img.resize((int(width * ratio), int(height * ratio)), PImage.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, "PNG")

        return buf.getvalue()
