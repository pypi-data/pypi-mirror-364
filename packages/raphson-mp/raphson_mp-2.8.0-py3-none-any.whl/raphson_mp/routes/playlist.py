from __future__ import annotations
import asyncio
from sqlite3 import Connection
from typing import TYPE_CHECKING, cast

from aiohttp import web

from raphson_mp import db, util
from raphson_mp.auth import User
from raphson_mp.common import metadata
from raphson_mp.common.playlist import PlaylistDict
from raphson_mp.common.tag import TagMode
from raphson_mp.decorators import route
from raphson_mp.playlist import Playlist, PlaylistStats, get_playlists
from raphson_mp.response import template

if TYPE_CHECKING:
    from raphson_mp.spotify import SpotifyTrack


# TODO move playlist management to separate module (not needed in offline mode)
@route("/manage")
async def route_playlists(_request: web.Request, conn: Connection, user: User):
    """
    Playlist management page
    """
    from raphson_mp import spotify
    spotify_client = spotify.client()
    playlists = get_playlists(conn, user)

    return await template(
        "playlists.jinja2",
        user_is_admin=user.admin,
        playlists=playlists,
        spotify_available=spotify_client is not None,
    )


@route("/stats")
async def route_stats(_request: web.Request, conn: Connection, user: User):
    playlists_stats: list[PlaylistStats] = []
    for playlist in get_playlists(conn):
        await asyncio.sleep(0)  # yield to event loop
        playlists_stats.append(playlist.stats())

    return await template(
        "playlists_stats.jinja2",
        user_is_admin=user.admin,
        playlists_stats=playlists_stats,
    )


@route("/favorite", method="POST")
async def route_favorite(request: web.Request, _conn: Connection, user: User):
    """
    Form target to mark a playlist as favorite.
    """
    form = await request.post()
    playlist = cast(str, form["playlist"])
    is_favorite = cast(str, form["favorite"])
    with db.connect() as writable_conn:
        if is_favorite == "1":
            writable_conn.execute(
                """
                INSERT INTO user_playlist_favorite
                VALUES (?, ?)
                ON CONFLICT DO NOTHING
                """,
                (user.user_id, playlist),
            )
        else:
            writable_conn.execute(
                """
                DELETE FROM user_playlist_favorite
                WHERE user=? AND playlist=?
                """,
                (user.user_id, playlist),
            )

    raise web.HTTPSeeOther("/playlist/manage")


@route("/share")
async def route_share_get(request: web.Request, conn: Connection, _user: User):
    """
    Page to select a username to share the provided playlist with
    """
    usernames = [row[0] for row in conn.execute("SELECT username FROM user")]
    csrf = request.query["csrf"]
    playlist_relpath = request.query["playlist"]
    return await template("playlists_share.jinja2", csrf=csrf, playlist=playlist_relpath, usernames=usernames)


@route("/share", method="POST")
async def route_share_post(request: web.Request, conn: Connection, user: User):
    """
    Form target to submit the selected username
    """
    form = await request.post()
    playlist_name = cast(str, form["playlist"])
    username = cast(str, form["username"])

    (target_user_id,) = conn.execute("SELECT id FROM user WHERE username=?", (username,)).fetchone()

    # Verify playlist exists and user has write access
    playlist = Playlist(conn, playlist_name, user)
    if not playlist.is_writable():
        raise web.HTTPForbidden(reason="Cannot share playlist if you do not have write permission")

    with db.connect() as writable_conn:
        writable_conn.execute(
            "INSERT INTO user_playlist_write VALUES(?, ?) ON CONFLICT DO NOTHING", (target_user_id, playlist_name)
        )

    raise web.HTTPSeeOther("/playlist/manage")


@route("/list")
async def route_list(_request: web.Request, conn: Connection, user: User):
    playlists = get_playlists(conn, user)
    json: list[PlaylistDict] = [
        {
            "name": playlist.name,
            "track_count": playlist.track_count,
            "favorite": playlist.is_favorite(),
            "write": playlist.is_writable(),
        }
        for playlist in playlists
    ]
    return web.json_response(json)


@route("/{playlist}/choose_track", method="POST")
async def route_track(request: web.Request, conn: Connection, user: User):
    """
    Choose random track from the provided playlist directory.
    """
    playlist_name = request.match_info["playlist"]
    playlist = Playlist(conn, playlist_name)
    json = await request.json()
    require_metadata: bool = cast(bool, json["require_metadata"]) if "require_metadata" in json else False

    if "tag_mode" in json:
        tag_mode = TagMode(cast(str, json["tag_mode"]))
        tags = cast(list[str], json["tags"])
        chosen_track = await playlist.choose_track(
            user, require_metadata=require_metadata, tag_mode=tag_mode, tags=tags
        )
    else:
        chosen_track = await playlist.choose_track(user, require_metadata=require_metadata)

    if chosen_track is None:
        raise web.HTTPNotFound(reason="no track found")

    return web.json_response(chosen_track.to_dict())


def _fuzzy_match_track(
    spotify_normalized_title: str, local_track_key: tuple[str, tuple[str, ...]], spotify_track: SpotifyTrack
) -> bool:
    (local_track_normalized_title, local_track_artists) = local_track_key
    if not util.str_match(spotify_normalized_title, local_track_normalized_title):
        return False

    # Title matches, now check if artist matches (more expensive)
    for artist_a in spotify_track.artists:
        for artist_b in local_track_artists:
            if util.str_match(artist_a, artist_b):
                return True

    return False


@route("/{playlist}/compare_spotify")
async def route_compare_spotify(request: web.Request, conn: Connection, _user: User):
    from raphson_mp import spotify
    playlist_name = request.match_info["playlist"]

    local_tracks: dict[tuple[str, tuple[str, ...]], tuple[str, list[str]]] = {}

    for title, artists in conn.execute(
        """
        SELECT title, GROUP_CONCAT(artist, ';') AS artists
        FROM track JOIN track_artist ON track.path = track_artist.track
        WHERE track.playlist = ?
        GROUP BY track.path
        """,
        (playlist_name,),
    ):
        local_track = (title, artists.split(";"))
        key = (metadata.normalize_title(title), tuple(local_track[1]))
        local_tracks[key] = local_track

    playlist_id = request.query["playlist_id"]

    duplicate_check: set[str] = set()
    duplicates: list[SpotifyTrack] = []
    both: list[tuple[tuple[str, list[str]], SpotifyTrack]] = []
    only_spotify: list[SpotifyTrack] = []
    only_local: list[tuple[str, list[str]]] = []

    spotify_client = spotify.client()
    if spotify_client is None:
        raise web.HTTPBadRequest(text='Spotify API is not available')

    i = 0
    async for spotify_track in spotify_client.get_playlist(playlist_id):
        i += 1
        if i % 10 == 0:
            await asyncio.sleep(0)  # yield to event loop

        normalized_title = metadata.normalize_title(spotify_track.title)

        # Spotify duplicates
        duplicate_check_entry = spotify_track.display
        if duplicate_check_entry in duplicate_check:
            duplicates.append(spotify_track)
        duplicate_check.add(duplicate_check_entry)

        # Try to find fast exact match
        local_track_key = (normalized_title, tuple(spotify_track.artists))
        if local_track_key in local_tracks:
            local_track = local_tracks[local_track_key]
        else:
            # Cannot find exact match, look for partial match
            for local_track_key in local_tracks.keys():
                if _fuzzy_match_track(normalized_title, local_track_key, spotify_track):
                    break
            else:
                # no match found
                only_spotify.append(spotify_track)
                continue

        # match found, present in both
        both.append((local_tracks[local_track_key], spotify_track))
        del local_tracks[local_track_key]

    # any local tracks still left in the dict must have no matching spotify track
    only_local.extend(local_tracks.values())

    return await template(
        "spotify_compare.jinja2", duplicates=duplicates, both=both, only_local=only_local, only_spotify=only_spotify
    )
