# Also update TrackJson in static/js/types.d.ts
from typing import NotRequired, TypedDict


class TrackDict(TypedDict):
    path: str
    mtime: int
    ctime: int
    duration: int
    title: NotRequired[str | None]
    album: NotRequired[str | None]
    album_artist: NotRequired[str | None]
    year: NotRequired[int | None]
    track_number: NotRequired[int | None]
    artists: NotRequired[list[str]]
    tags: NotRequired[list[str]]
    video: NotRequired[str | None]
    lyrics: NotRequired[str | None]


class QueuedTrackDict(TypedDict):
    track: TrackDict
    manual: bool


class FilterResponseDict(TypedDict):
    tracks: list[TrackDict]


class DislikesResponseDict(TypedDict):
    tracks: list[TrackDict]


class GetCsrfResponseDict(TypedDict):
    token: str
