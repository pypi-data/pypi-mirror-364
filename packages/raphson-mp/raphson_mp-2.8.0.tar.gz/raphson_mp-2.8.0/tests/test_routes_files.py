from aiohttp.web import HTTPBadRequest
from raphson_mp import util
from raphson_mp.client.track import Track
from tests import T_client, assert_html, get_csrf


async def test_files(client: T_client):
    await assert_html(client, "/files")


async def test_rename(client: T_client, track: Track):
    await assert_html(client, "/files/rename?path=" + util.urlencode(track.path))


async def test_mkdir_exists(client: T_client, playlist: str):
    csrf = await get_csrf(client)
    async with client.post('/files/mkdir', data={'path': '', 'dirname': playlist, 'csrf': csrf}) as response:
        assert response.status == HTTPBadRequest.status_code
        assert "already exists" in await response.text()


async def test_download_file(client: T_client, track: Track):
    async with client.get("/files/download", params={"path": track.path}) as response:
        response.raise_for_status()


async def test_download_playlist(client: T_client, playlist: str):
    async with client.get("/files/download", params={"path": playlist}) as response:
        response.raise_for_status()
        while _data := await response.content.read(1024*1024):
            pass
