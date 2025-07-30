import pytest

from raphson_mp import lyrics
from raphson_mp.common.lyrics import LyricsLine, PlainLyrics, TimeSyncedLyrics
from raphson_mp.lyrics import AZLyricsFetcher, GeniusFetcher, LrcLibFetcher


def test_fixup():
    lyr = PlainLyrics("Source", "е")
    lyrics._fixup(lyr)
    assert lyr == PlainLyrics("Source", "e")

    lyr = TimeSyncedLyrics("Source", [LyricsLine(0, "е")])
    lyrics._fixup(lyr)
    assert lyr == TimeSyncedLyrics("Source", [LyricsLine(0, "e")])


@pytest.mark.online
async def test_lrclib():
    # full length cd version
    lyrics = await LrcLibFetcher().find("Strong", "London Grammar", "If You Wait", 276)
    assert isinstance(lyrics, TimeSyncedLyrics), lyrics
    assert lyrics.text[0].text == "Excuse me for a while", lyrics.text[0]
    assert lyrics.text[0].start_time == 43.56, lyrics.text[0]

    # music video version
    lyrics = await LrcLibFetcher().find("Strong", "London Grammar", "If You Wait", 242)
    assert isinstance(lyrics, TimeSyncedLyrics), lyrics
    assert lyrics.text[0].text == "Excuse me for a while", lyrics.text[0]
    assert lyrics.text[0].start_time == 14.6, lyrics.text[0]


@pytest.mark.online
async def test_azlyrics():
    lyrics = await AZLyricsFetcher().find("Starburster", "Fontaines D.C.", None, None)
    assert isinstance(lyrics, PlainLyrics)
    assert "I wanna see you alone, I wanna sharp the stone" in lyrics.text, lyrics.text


@pytest.mark.online
async def test_genius():
    lyrics = await GeniusFetcher().find("Give Me One Reason", "Tracy Chapman", None, None)
    assert isinstance(lyrics, PlainLyrics)
    assert "You know that I called you, I called too many times" in lyrics.text, lyrics.text


# @pytest.mark.online
# async def test_lyricfind():
#     lyrics = await LyricFindFetcher().find("Blank Space", "Taylor Swift", None, None)
#     assert isinstance(lyrics, PlainLyrics)
#     assert "Nice to meet you, where you been?" in lyrics.text, lyrics.text
