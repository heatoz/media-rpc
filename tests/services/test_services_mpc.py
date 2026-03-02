from mpcrpc.core.models import PlaybackState

from mpcrpc.core.events import PlaybackSessionUpdated, PlaybackFileUpdated

from unittest.mock import AsyncMock, MagicMock, patch

from mpcrpc.infra import EventBus
from mpcrpc.services import MPC

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_variables_html(
    file: str = "movie.mkv",
    state: int = 2,
    position: int = 10000,
    duration: int = 4630005,
) -> str:
    return (
        f'<p id="file">{file}</p>'
        f'<p id="state">{state}</p>'
        f'<p id="position">{position}</p>'
        f'<p id="duration">{duration}</p>'
    )


def make_p_data(
    file: str = "movie.mkv",
    state: int = 2,
    position: int = 10000,
    duration: int = 4630005,
) -> dict:
    return {
        "file": file,
        "state": str(state),
        "position": str(position),
        "duration": str(duration),
    }


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def event_bus():
    bus = MagicMock(spec=EventBus)
    bus.publish = AsyncMock()
    return bus


@pytest.fixture
def mpc(event_bus):
    with patch("mpcrpc.services.mpc.HttpClient") as MockHttpClient:
        MockHttpClient.return_value = MagicMock()
        instance = MPC(event_bus=event_bus, port=13579)
    return instance


# ---------------------------------------------------------------------------
# Helpers: call_variables and warm_up
# ---------------------------------------------------------------------------


async def call_variables(mpc_instance, p_data: dict):
    """
    Patches HttpClient.get and Regex.Variables so Variables() uses p_data
    without a real HTTP call.
    """
    html = make_variables_html(
        file=p_data["file"],
        state=int(p_data["state"]),
        position=int(p_data["position"]),
        duration=int(p_data["duration"]),
    )
    with (
        patch.object(mpc_instance._client, "get", new=AsyncMock(return_value=html)),
        patch("mpcrpc.services.mpc.Regex.Variables", return_value=p_data),
    ):
        await mpc_instance.Variables()


async def warm_up(mpc_instance, event_bus, p_data: dict, ts: float = 100.0):
    """
    Fully primes both c_session and c_file caches so tests start from a
    stable, realistic state.

    How it works:
      Call 1 (t=ts):     no c_session → session branch fires, c_file still None.
      Call 2 (t=ts+1.0): session unchanged, position naturally advanced,
                          c_file is None → file branch fires, c_file cached.

    After both calls event_bus.publish is reset so the test starts clean.
    """
    with patch("mpcrpc.services.mpc.time.monotonic", return_value=ts):
        await call_variables(mpc_instance, p_data)

    # Advance position by exactly 1000ms (1 s elapsed) — well within threshold
    p_data_2 = {**p_data, "position": str(int(p_data["position"]) + 1000)}
    with patch("mpcrpc.services.mpc.time.monotonic", return_value=ts + 1.0):
        await call_variables(mpc_instance, p_data_2)

    event_bus.publish.reset_mock()


# ---------------------------------------------------------------------------
# 1. First call — no cache — should always publish PlaybackSessionUpdated
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_first_call_publishes_session_updated(mpc, event_bus):
    await call_variables(mpc, make_p_data())

    event_bus.publish.assert_awaited_once()
    event = event_bus.publish.call_args[0][0]
    assert isinstance(event, PlaybackSessionUpdated)
    assert event.p_session.state == PlaybackState.PLAYING
    assert event.p_session.pos == 10000


# ---------------------------------------------------------------------------
# 2. No change between polls — nothing published
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_no_change_publishes_nothing(mpc, event_bus):
    base = make_p_data(position=10000)
    await warm_up(mpc, event_bus, base, ts=100.0)

    # Position naturally advances ~1s worth — well within threshold
    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(position=12000))

    event_bus.publish.assert_not_awaited()


# ---------------------------------------------------------------------------
# 3. State change (playing → paused) — should publish PlaybackSessionUpdated
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_state_change_publishes_session_updated(mpc, event_bus):
    await warm_up(mpc, event_bus, make_p_data(state=2, position=10000))

    await call_variables(mpc, make_p_data(state=1, position=10500))

    event_bus.publish.assert_awaited_once()
    event = event_bus.publish.call_args[0][0]
    assert isinstance(event, PlaybackSessionUpdated)
    assert event.p_session.state == PlaybackState.PAUSED


# ---------------------------------------------------------------------------
# 4. Forward seek (large position jump) — should publish PlaybackSessionUpdated
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_forward_seek_publishes_session_updated(mpc, event_bus):
    await warm_up(mpc, event_bus, make_p_data(position=10000), ts=100.0)

    # 1s later, but position jumped 60s — deviation >> 3000ms threshold
    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(position=70000))

    event_bus.publish.assert_awaited_once()
    assert isinstance(event_bus.publish.call_args[0][0], PlaybackSessionUpdated)


# ---------------------------------------------------------------------------
# 5. Backward seek — should publish PlaybackSessionUpdated
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_backward_seek_publishes_session_updated(mpc, event_bus):
    await warm_up(mpc, event_bus, make_p_data(position=60000), ts=100.0)

    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(position=30000))  # went backward

    event_bus.publish.assert_awaited_once()
    assert isinstance(event_bus.publish.call_args[0][0], PlaybackSessionUpdated)


# ---------------------------------------------------------------------------
# 6. File change — should publish PlaybackFileUpdated
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_file_change_publishes_file_updated(mpc, event_bus):
    await warm_up(
        mpc, event_bus, make_p_data(file="movie_a.mkv", position=10000), ts=100.0
    )

    # Same state, position naturally advanced, but different file
    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(file="movie_b.mkv", position=12000))

    event_bus.publish.assert_awaited_once()
    event = event_bus.publish.call_args[0][0]
    assert isinstance(event, PlaybackFileUpdated)
    assert event.p_file.name == "movie_b.mkv"


# ---------------------------------------------------------------------------
# 7. Seek takes priority over file check — only SessionUpdated published
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_seek_takes_priority_over_file_change(mpc, event_bus):
    """
    If both a seek and a file change are detected in the same poll,
    only PlaybackSessionUpdated should be published (early return).
    """
    await warm_up(mpc, event_bus, make_p_data(file="a.mkv", position=10000), ts=100.0)

    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        # Different file AND a large position jump (seek)
        await call_variables(mpc, make_p_data(file="b.mkv", position=80000))

    assert event_bus.publish.await_count == 1
    assert isinstance(event_bus.publish.call_args[0][0], PlaybackSessionUpdated)


# ---------------------------------------------------------------------------
# 8. Seek detection is skipped when player is paused
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_seek_not_detected_when_paused(mpc, event_bus):
    """
    Seek detection only triggers when state == PLAYING.
    A position jump while paused should NOT be treated as a seek.
    """
    await warm_up(mpc, event_bus, make_p_data(state=1, position=10000), ts=100.0)

    # Position jumps while still paused — no seek, no state change
    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(state=1, position=80000))

    event_bus.publish.assert_not_awaited()


# ---------------------------------------------------------------------------
# 9. Cache is updated after session event
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_updated_after_session_event(mpc, event_bus):
    await call_variables(mpc, make_p_data(position=5000))

    cached = mpc._cache.get("c_session")
    assert cached is not None
    assert cached.pos == 5000
    assert mpc._cache.get("c_session_ts") is not None


# ---------------------------------------------------------------------------
# 10. Cache is updated after file event
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cache_updated_after_file_event(mpc, event_bus):
    await warm_up(mpc, event_bus, make_p_data(file="old.mkv", position=10000), ts=100.0)

    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(file="new.mkv", position=12000))

    cached_file = mpc._cache.get("c_file")
    assert cached_file is not None
    assert cached_file.name == "new.mkv"


# ---------------------------------------------------------------------------
# 11. Position within natural drift threshold is NOT treated as a seek
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_position_within_threshold_not_a_seek(mpc, event_bus):
    """
    abs(p_pos - (c_pos + elapsed * 1000)) must exceed 3000 to be a seek.
    A 200ms drift should not trigger it.
    """
    await warm_up(mpc, event_bus, make_p_data(position=10000), ts=100.0)

    # elapsed=2s, expected=12000 (from warm_up second call pos=11000, ts=101),
    # actual=12200 — drift of 200ms
    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(position=12200))

    event_bus.publish.assert_not_awaited()


# ---------------------------------------------------------------------------
# 12. Position drift exactly at threshold boundary (3000ms) is NOT a seek
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_position_at_threshold_boundary_not_a_seek(mpc, event_bus):
    """
    After warm_up the cached session has pos=11000 at ts=101.0.
    At ts=102.0, elapsed=1s, expected=12000, actual=15000 → drift=3000 — NOT above threshold.
    """
    await warm_up(mpc, event_bus, make_p_data(position=10000), ts=100.0)

    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(position=15000))

    event_bus.publish.assert_not_awaited()


# ---------------------------------------------------------------------------
# 13. Position drift just above threshold (3001ms) IS a seek
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_position_just_above_threshold_is_a_seek(mpc, event_bus):
    """
    After warm_up the cached session has pos=11000 at ts=101.0.
    At ts=102.0, elapsed=1s, expected=12000, actual=15001 → drift=3001 — above threshold.
    """
    await warm_up(mpc, event_bus, make_p_data(position=10000), ts=100.0)

    with patch("mpcrpc.services.mpc.time.monotonic", return_value=102.0):
        await call_variables(mpc, make_p_data(position=15001))

    event_bus.publish.assert_awaited_once()
    assert isinstance(event_bus.publish.call_args[0][0], PlaybackSessionUpdated)
