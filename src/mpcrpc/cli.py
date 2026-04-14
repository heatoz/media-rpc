from mpcrpc.infra.uploaders import Litterbox, ImgBB, Imgur
from mpcrpc.infra.adapters import IMDB, TMDB, MAL
from mpcrpc.services import MPC, Media, RPC
from mpcrpc.infra import EventBus

from pathlib import Path
import traceback
import asyncio
import tomllib

DISCORD_CLIENT_ID: int = 1411516401541185566
CONFIG_PATH: Path = Path("./config.toml")


class Config:
    """
    Represents a configuration state.
    """

    def __init__(
        self,
        port: int,
        adapter: str,
        adapter_token: str | None,
        uploader: str,
        uploader_token: str | None,
    ) -> None:
        """
        Initializes a Configuration instance.

        Args:
            port (int):
                The MPC-HC Web Interface port.

            adapter (str):
                The adapter name to parse media from.

            adapter_token (str, optional):
                The API token for the adapter, if required.

            uploader (str):
                The uploader name to host images.

            uploader_token (str, optional):
                The API token for the uploader, if required.
        """

        self.port: int = port
        self.adapter: str = adapter
        self.adapter_token: str | None = adapter_token
        self.uploader: str = uploader
        self.uploader_token: str | None = uploader_token


DEFAULT_CONFIG = """\
[mpc]
port = 13579

[adapter]
name = "imdb"
# name = "tmdb"
# token = "your_token_here"
# name = "mal"
# ...

[uploader]
name = "litterbox"
# name = "imgbb"
# token = "your_token_here"
# ...
"""


def _load_config() -> Config:
    """
    Load the configuration from the TOML file.

    If the config file does not exist, a default one is created
    and the program exits, prompting the user to edit it.

    Returns:
        Config:
            The loaded configuration state.
    """

    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(DEFAULT_CONFIG)
        raise SystemExit(f"Config file created at {CONFIG_PATH}\n")

    with CONFIG_PATH.open("rb") as f:
        raw = tomllib.load(f)

    return Config(
        port=raw.get("mpc", {}).get("port", 13579),
        adapter=raw["adapter"]["name"],
        adapter_token=raw["adapter"].get("token"),
        uploader=raw["uploader"]["name"],
        uploader_token=raw["uploader"].get("token"),
    )


def _build_adapter(config: Config) -> object:
    """
    Build the media adapter from the given configuration.

    Args:
        config (Config):
            The loaded configuration state.

    Returns:
        object:
            The instantiated adapter.
    """

    if config.adapter == "tmdb":
        if not config.adapter_token:
            raise ValueError("TMDB adapter requires a token in config.toml")
        return TMDB(token=config.adapter_token)

    if config.adapter == "imdb":
        return IMDB()

    if config.adapter == "mal":
        return MAL()

    raise ValueError(f"Unknown adapter: {config.adapter}")


def _build_uploader(config: Config) -> object:
    """
    Build the image uploader from the given configuration.

    Args:
        config (Config):
            The loaded configuration state.

    Returns:
        object:
            The instantiated uploader.
    """

    if config.uploader == "imgbb":
        if not config.uploader_token:
            raise ValueError("ImgBB uploader requires a token in config.toml")
        return ImgBB(token=config.uploader_token)

    if config.uploader == "litterbox":
        return Litterbox()

    if config.uploader == "imgur":
        if not config.uploader_token:
            raise ValueError("Imgur uploader requires a token in config.toml")
        return ImgBB(token=config.uploader_token)

    raise ValueError(f"Unknown uploader: {config.uploader}")


async def _poll(mpc: MPC) -> None:
    """
    Runs a continuous MPC-HC polling loop.

    Args:
        mpc (MPC):
            A MPC Service instance.
    """

    while True:
        try:
            await mpc.Variables()
        except Exception:
            print("Error:", traceback.format_exc())

        await asyncio.sleep(3)


async def _cli() -> None:
    """
    MPC-RPC Entry Point
    """

    config = _load_config()

    event_bus: EventBus = EventBus()
    mpc: MPC = MPC(event_bus, config.port)
    rpc: RPC = RPC(event_bus)

    adapter = _build_adapter(config)
    uploader = _build_uploader(config)
    Media(event_bus, adapter, uploader)

    await rpc.start(DISCORD_CLIENT_ID)

    asyncio.create_task(_poll(mpc))
    await asyncio.Event().wait()


def main() -> None:
    """
    CLI entry point.
    """

    asyncio.run(_cli())


if __name__ == "__main__":
    main()
