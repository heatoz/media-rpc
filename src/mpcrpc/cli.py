from mpcrpc.services import MPC, Media, RPC
from mpcrpc.infra.adapters import IMDB, TMDB, MAL
from mpcrpc.infra import EventBus

import traceback
import argparse
import asyncio

# mpc-hc discord application id.
DISCORD_CLIENT_ID: int = 1411516401541185566


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Discord Rich Presence integration for MPC-HC",
    )

    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=13579,
        help="MPC-HC Web Interface port [default: 13579]",
    )

    parser.add_argument(
        "-a",
        "--adapter",
        required=True,
        choices=["imdb", "tmdb", "mal"],
        help="The adapter the medias are going to be parsed from",
    )

    parser.add_argument(
        "--token",
        required=False,
        help="API token [required for some adapters]",
    )

    return parser


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
    Starts the MPC-RPC service, initializing the event bus,
    registering services, and polling MPC-HC for playback updates.
    """

    parser = _build_parser()
    args = parser.parse_args()

    if args.adapter == "tmdb" and not args.token:
        parser.error("The TMDB adapter requires an API token, please use --token")

    adapter = {
        "imdb": lambda: IMDB(),
        "tmdb": lambda: TMDB(token=args.token),
        "mal": lambda: MAL(),
    }[args.adapter]()

    event_bus: EventBus = EventBus()

    mpc: MPC = MPC(event_bus, args.port)
    rpc: RPC = RPC(event_bus)

    Media(event_bus, adapter)

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
