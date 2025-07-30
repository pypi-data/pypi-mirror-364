import asyncio
import itertools
import math
from pathlib import Path
import tempfile

from raphson_mp import db, ffmpeg
from raphson_mp import settings
from raphson_mp.client.track import Track
from raphson_mp.common.image import ImageFormat, ImageQuality
from raphson_mp.common.track import AudioFormat
from raphson_mp.track import FileTrack, from_relpath


async def test_thumbnail():
    image = Path("docs/tyrone_music.jpg").read_bytes()
    options = itertools.product(ImageFormat, ImageQuality, [True, False])
    thumbnails = await asyncio.gather(
        *[ffmpeg.image_thumbnail(image, img_format, img_quality, square) for img_format, img_quality, square in options]
    )
    results = await asyncio.gather(*[ffmpeg.check_image(thumbnail) for thumbnail in thumbnails])
    assert all(results)


async def test_corrupt_image():
    assert await ffmpeg.check_image(b"not an image!") is False


async def test_transcode_opus_loudness(track: Track):
    input_path = from_relpath(track.path)

    loudness = await ffmpeg.measure_loudness(input_path)
    assert loudness is not None

    with tempfile.NamedTemporaryFile() as output_tempfile:
        output_path = Path(output_tempfile.name)
        await ffmpeg.transcode_audio(input_path, loudness, AudioFormat.WEBM_OPUS_HIGH, output_path)
        await ffmpeg.transcode_audio(input_path, loudness, AudioFormat.WEBM_OPUS_LOW, output_path)

        # measure output loudness, should be close to loudness target
        loudness2 = await ffmpeg.measure_loudness(output_path)
        assert loudness2 is not None
        assert math.isclose(loudness2["input_i"], ffmpeg._LOUDNORM_I, abs_tol=0.3), loudness2


async def test_transcode_mp3(track: Track):
    with db.connect(read_only=True) as conn:
        server_track = FileTrack(conn, track.path)

    with tempfile.NamedTemporaryFile() as output_tempfile:
        output_path = Path(output_tempfile.name)

        loudness = await ffmpeg.measure_loudness(server_track.filepath)
        await ffmpeg.transcode_audio(
            server_track.filepath, loudness, AudioFormat.MP3_WITH_METADATA, output_path, server_track
        )


async def test_probe_corrupt():
    meta = await ffmpeg.probe_metadata(Path("babel.cfg"))
    assert meta is None


async def test_probe_image():
    meta = await ffmpeg.probe_metadata(settings.raphson_png)
    assert meta is None


async def test_probe():
    meta = await ffmpeg.probe_metadata(Path("tests/data/test.mp3"))
    assert meta is not None
    assert meta.title == "TestTitle"
    assert meta.artists == ["TestArtist1", "TestArtist2"]
    assert meta.album == "TestAlbum"
    assert meta.album_artist == "TestAlbumArtist"
    assert meta.tags == ["TestGenre1", "TestGenre2"]
    assert meta.track_number == 24
    assert meta.year == 2000
    assert meta.duration == 7
