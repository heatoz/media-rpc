from media_rpc.infra.uploaders import Litterbox, ImgBB, Imgur, OnlyImage
from media_rpc.services.players import MPC, Jellyfin, Plex, VLC
from media_rpc.infra.adapters import IMDB, TMDB, MAL
from media_rpc.services import Media, RPC
from media_rpc.infra import EventBus

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
        player: str,
        player_options: dict,
        adapter: str,
        adapter_token: str | None,
        uploader: str,
        uploader_token: str | None,
    ) -> None:
        self.player: str = player
        self.player_options: dict = player_options
        self.adapter: str = adapter
        self.adapter_token: str | None = adapter_token
        self.uploader: str = uploader
        self.uploader_token: str | None = uploader_token


DEFAULT_CONFIG = """\
[player]
name = "mpc"
# port = 13579  # optional, defaults to 13579

# name = "jellyfin"
# host = "localhost"
# token = "your_token_here"
# user_name = "your_username"
# port = 8096  # optional, defaults to 8096
# ...

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
    Loads configuration from a file.

    Returns:
        Config:
            A Config object.
    """

    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(DEFAULT_CONFIG)
        raise SystemExit(f"Config file created at {CONFIG_PATH}\n")

    with CONFIG_PATH.open("rb") as f:
        raw = tomllib.load(f)

    player_raw = raw.get("player", {})

    return Config(
        player=player_raw["name"],
        player_options={k: v for k, v in player_raw.items() if k != "name"},
        adapter=raw["adapter"]["name"],
        adapter_token=raw["adapter"].get("token"),
        uploader=raw["uploader"]["name"],
        uploader_token=raw["uploader"].get("token"),
    )


def _build_adapter(config: Config) -> object:
    """
    Build the adapter instance from the given configuration.

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
    Build the uploader instance from the given configuration.

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
        return Imgur(token=config.uploader_token)

    if config.uploader == "onlyimage":
        if not config.uploader_token:
            raise ValueError("OnlyImage uploader requires a token in config.toml")
        return OnlyImage(token=config.uploader_token)

    raise ValueError(f"Unknown uploader: {config.uploader}")


def _build_player(config: Config, event_bus: EventBus) -> object:
    """
    Build the player instance from the given configuration.

    Args:
        config (Config):
            The loaded configuration state.

        event_bus (EventBus):
            The shared event bus instance.

    Returns:
        object:
            The instantiated player.
    """

    opts = config.player_options

    if config.player == "mpc":
        kwargs = {}
        
        if "host" in opts:
            kwargs["host"] = opts["host"]

        if "port" in opts:
            kwargs["port"] = opts["port"]

        return MPC(event_bus, **kwargs)

    if config.player == "jellyfin":
        for required in ("token", "user_name"):
            if required not in opts:
                raise ValueError(
                    f"Jellyfin player requires '{required}' in config.toml"
                )

        kwargs = {
            "token": opts["token"],
            "user_name": opts["user_name"]
        }

        if "host" in opts:
            kwargs["host"] = opts["host"]

        if "port" in opts:
            kwargs["port"] = opts["port"]

        return Jellyfin(event_bus, **kwargs)

    if config.player == "plex":
        for required in ("token", "user_name"):
            if required not in opts:
                raise ValueError(
                    f"Plex player requires '{required}' in config.toml"
                )

        kwargs = {
            "token": opts["token"],
            "user_name": opts["user_name"]
        }

        if "host" in opts:
            kwargs["host"] = opts["host"]

        if "port" in opts:
            kwargs["port"] = opts["port"]

        return Plex(event_bus, **kwargs)

    if config.player == "vlc":
        kwargs = {}
        
        if "password" not in opts:
            raise ValueError(
                "VLC player requires 'password' in config.toml"
            )
        
        kwargs["password"] = opts["password"]

        if "host" in opts:
            kwargs["host"] = opts["host"]

        if "port" in opts:
            kwargs["port"] = opts["port"]

        return VLC(event_bus, **kwargs)

    raise ValueError(f"Unknown player: {config.player!r}")


async def _poll(player: object) -> None:
    """
    Runs a continuous polling loop for the active player.

    Args:
        player (object):
            A player service instance.
    """

    if isinstance(player, MPC):
        poll = player.Variables
    elif isinstance(player, Jellyfin):
        poll = player.Sessions
    elif isinstance(player, Plex):
        poll = player.Sessions
    elif isinstance(player, VLC):
        poll = player.Status
    else:
        raise TypeError(f"Unsupported player type: {type(player)!r}")

    while True:
        try:
            await poll()
        except Exception:
            print("Error:", traceback.format_exc())

        await asyncio.sleep(3)


async def _cli() -> None:
    """
    media-rpc Entry Point
    """

    config = _load_config()

    event_bus: EventBus = EventBus()
    rpc: RPC = RPC(event_bus)

    adapter = _build_adapter(config)
    uploader = _build_uploader(config)
    Media(event_bus, adapter, uploader)

    player = _build_player(config, event_bus)

    await rpc.start(DISCORD_CLIENT_ID)

    asyncio.create_task(_poll(player))
    await asyncio.Event().wait()


def main() -> None:
    asyncio.run(_cli())


if __name__ == "__main__":
    main()
