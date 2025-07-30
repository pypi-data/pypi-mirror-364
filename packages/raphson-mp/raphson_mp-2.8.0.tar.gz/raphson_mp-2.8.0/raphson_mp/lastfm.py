import hashlib
import logging
from typing import Any

from raphson_mp import db, httpclient, ratelimit, settings
from raphson_mp.auth import StandardUser
from raphson_mp.common import metadata
from raphson_mp.common.track import VIRTUAL_PLAYLIST
from raphson_mp.track import Track
from raphson_mp.util import urlencode

log = logging.getLogger(__name__)


if settings.offline_mode:
    # Module must not be imported to ensure no data is ever downloaded in offline mode.
    raise RuntimeError("Cannot use last.fm in offline mode")


def get_connect_url() -> str | None:
    if not settings.lastfm_api_key:
        return None

    return "https://www.last.fm/api/auth/?api_key=" + settings.lastfm_api_key


def is_configured() -> bool:
    """Check whether last.fm API key is set"""
    return bool(settings.lastfm_api_key) and bool(settings.lastfm_api_secret)


async def _make_request(method: str, api_method: str, **extra_params: str) -> dict[str, Any]:
    async with ratelimit.LASTFM:
        if not settings.lastfm_api_key or not settings.lastfm_api_secret:
            raise ValueError("no lastfm api key")

        params: dict[str, str] = {
            "api_key": settings.lastfm_api_key,
            "method": api_method,
            "format": "json",
            **extra_params,
        }
        # last.fm API requires alphabetically sorted parameters for signature
        items = sorted(params.items())
        query_string = "&".join(f"{urlencode(k)}={urlencode(v)}" for k, v in items)
        secret = settings.lastfm_api_secret.encode()
        sig = b"".join(f"{k}{v}".encode() for k, v in items if k != "format") + secret
        sig_digest = hashlib.md5(sig).hexdigest()
        query_string += f"&api_sig={sig_digest}"
        async with httpclient.session("https://ws.audioscrobbler.com/2.0/") as session:
            if method == "post":
                async with session.post(
                    "",
                    data=query_string,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                ) as response:
                    return await response.json()
            elif method == "get":
                async with session.get("?" + query_string) as response:
                    return await response.json()
            else:
                raise ValueError()


def get_user_key(user: StandardUser) -> str | None:
    """
    Get a user's last.fm session key from local database
    Returns session key, or None if the user has not set up last.fm
    """
    with db.connect(read_only=True) as conn:
        result = conn.execute("SELECT key FROM user_lastfm WHERE user=?", (user.user_id,)).fetchone()
    return result[0] if result else None


async def obtain_session_key(user: StandardUser, auth_token: str) -> str:
    """
    Fetches session key from last.fm API and saves it to the database
    Params:
        auth_token
    Returns: last.fm username
    """
    json = await _make_request("get", "auth.getSession", token=auth_token)
    name = json["session"]["name"]
    key = json["session"]["key"]
    user.conn.execute(
        "INSERT OR REPLACE INTO user_lastfm (user, name, key) VALUES (?, ?, ?)", (user.user_id, name, key)
    )

    return name


async def update_now_playing(user_key: str, track: Track):
    """Send now playing status to last.fm"""
    if not is_configured():
        log.info("Skipped update_now_playing, last.fm not configured")
        return

    artist = track.primary_artist

    if not artist or not track.title:
        log.info("Skipped update_now_playing, missing metadata")
        return

    log.info("Sending now playing to last.fm: %s", track.path)
    await _make_request("post", "track.updateNowPlaying", artist=artist, track=track.title, sk=user_key)


async def scrobble(user_key: str, track: Track, start_timestamp: int):
    """Send played track to last.fm"""
    if not is_configured():
        log.info("Skipped scrobble, last.fm not configured")
        return

    if track.playlist == VIRTUAL_PLAYLIST:
        log.info("Skipped scrobble for virtual track")
        return

    artist = track.primary_artist

    if not track.title or not artist:
        log.info("Skipped scrobble, missing metadata")
        return

    params = {
        "artist": artist,
        "track": track.title,
        "chosenByUser": "0",
        "timestamp": str(start_timestamp),
        "sk": user_key,
    }

    if track.album and not metadata.album_is_compilation(track.album):
        params["album"] = track.album

    await _make_request("post", "track.scrobble", **params)

    log.info("Scrobbled to last.fm: %s - %s", artist, track.title)
