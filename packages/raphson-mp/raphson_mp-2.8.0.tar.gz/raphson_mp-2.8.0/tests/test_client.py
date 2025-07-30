# pyright: reportUnreachable=false
import asyncio
import random
import time
from pathlib import Path
from typing import cast


from aiohttp.client import ClientResponseError
from raphson_mp import db, settings
from raphson_mp import activity
from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.track import Track
from raphson_mp.common.control import (
    ClientPlaying,
    ClientSubscribe,
    ServerCommand,
    ServerPlaying,
    Topic,
)
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import VIRTUAL_PLAYLIST, AudioFormat, TrackBase


def setup_module():
    settings.data_dir = Path("./data").resolve()
    settings.music_dir = Path("./music").resolve()

NEWS_TRACK = TrackBase(path=f"{VIRTUAL_PLAYLIST}/news", mtime=0, ctime=0, duration=10, title=None, album=None, album_artist=None, year=None, track_number=None, video=None, lyrics=None, artists=[], tags=[])


async def test_choose_track(music_client: RaphsonMusicClient, playlist: str):
    try:
        await music_client.choose_track(playlist)
    except ClientResponseError as ex:
        if ex.status == 404:
            # 404 is fine if playlist contains no tracks
            with db.connect(read_only=True) as conn:
                track_count = cast(int, conn.execute('SELECT COUNT(*) FROM track WHERE playlist=?', (playlist,)).fetchone()[0])
                assert track_count == 0
        else:
            raise ex


async def test_list_tracks(music_client: RaphsonMusicClient, nonempty_playlist: str):
    tracks = await music_client.list_tracks(nonempty_playlist)
    track = random.choice(tracks)
    await music_client.get_track(track.path)  # verify the track exists


async def test_download_cover(music_client: RaphsonMusicClient, track: Track):
    await asyncio.gather(
        *[
            track.get_cover_image(music_client, format=format, quality=quality, meme=meme)
            for format in ImageFormat
            for quality in ImageQuality
            for meme in (False, True)
        ]
    )


async def test_now_playing(music_client: RaphsonMusicClient, track: Track):
    expected_virtual = False
    received_events: int = 0

    async def handler(command: ServerCommand):
        if not isinstance(command, ServerPlaying):
            return

        nonlocal received_events
        received_events += 1

        assert abs(command.update_time - time.time()) < 1

        assert expected_virtual == (track.playlist == VIRTUAL_PLAYLIST)
        assert "path" in command.track
        assert command.control == False

    music_client.control_start(handler=handler)

    # Before subscription (should be received as soon as subscription is started)
    await music_client.control_send(ClientPlaying(track=track.to_dict(), paused=False, client="test"))

    # Subscribe now
    await music_client.control_send(ClientSubscribe(topic=Topic.ACTIVITY))

    # Wait for websocket receive
    async with asyncio.timeout(5):
        while received_events != 1:  # pyright: ignore[reportUnnecessaryComparison]
            await asyncio.sleep(0)

    # Send another track
    await music_client.control_send(
        ClientPlaying(track=track.to_dict(), paused=True, client="test")
    )

    # Wait for websocket receive
    async with asyncio.timeout(5):
        while received_events != 2:
            await asyncio.sleep(0)

    # Send news
    expected_virtual = True
    await music_client.control_send(
        ClientPlaying(track=NEWS_TRACK.to_dict(), paused=True, client="test")
    )

    # Wait for websocket receive
    async with asyncio.timeout(5):
        while received_events != 3:
            await asyncio.sleep(0)

    await music_client.control_stop()


async def test_stop(music_client: RaphsonMusicClient, track: Track):
    activity._NOW_PLAYING = {}
    music_client.control_start()
    await music_client.control_send(ClientPlaying(track=track.to_dict(), paused=False, client="test"))

    # wait for server to process ClientPlaying
    async with asyncio.timeout(1):
        while len(activity.now_playing()) == 0:
            await asyncio.sleep(0)

    # there should be 1 player playing
    assert len(activity.now_playing()) == 1
    await music_client.signal_stop()
    # now that player should be gone
    assert len(activity.now_playing()) == 0

    await music_client.control_stop()


# this test is at the end because it takes a while
async def test_download_audio(music_client: RaphsonMusicClient, track: Track):
    await asyncio.gather(*[track.get_audio(music_client, format) for format in AudioFormat])
