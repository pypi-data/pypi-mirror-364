from aiohttp import web

from raphson_mp.client import RaphsonMusicClient
from raphson_mp.client.track import Track
from tests import T_client


async def test_share(client: T_client, music_client: RaphsonMusicClient, track: Track):
    share = await track.share(music_client)
    share_code = share.share_code

    async with client.get("/share/" + share_code, allow_redirects=False) as response:
        assert response.status == web.HTTPSeeOther.status_code
        track_page = response.headers["Location"]

    async with client.get(track_page, raise_for_status=True) as response:
        pass

    async with client.get(f"{track_page}/cover", raise_for_status=True) as response:
        pass

    async with client.get(f"{track_page}/audio", raise_for_status=True) as response:
        pass

    async with client.get(f"{track_page}/download/mp3", raise_for_status=True) as response:
        pass

    async with client.get(f"{track_page}/download/original", raise_for_status=True) as response:
        pass
