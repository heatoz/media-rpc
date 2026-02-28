import pytest
from mpcrpc.utils import MediaFile, Regex  # adjust path as needed


# ---------------------------------------------------------------------------
# Sample HTML from MPC-HC /variables endpoint
# ---------------------------------------------------------------------------

VARIABLES_HTML = (
    '<!DOCTYPE html><html lang="en"><head></head><body class="page-variables">'
    '<p id="file">As.1001.Posicoes.do.Amor.1978.HDTVRip.x264-gooz.mkv</p>'
    '<p id="filepatharg">C:%5cUsers%5callan%5cDownloads%5cfile.mkv</p>'
    '<p id="filepath">C:\\Users\\allan\\Downloads\\file.mkv</p>'
    '<p id="filedirarg">C:%5cUsers%5callan%5cDownloads</p>'
    '<p id="filedir">C:\\Users\\allan\\Downloads</p>'
    '<p id="state">2</p>'
    '<p id="statestring">Reproduzindo</p>'
    '<p id="position">490945</p>'
    '<p id="positionstring">00:08:11</p>'
    '<p id="duration">4630005</p>'
    '<p id="durationstring">01:17:10</p>'
    '<p id="volumelevel">70</p>'
    '<p id="muted">0</p>'
    '</body></html>'
)


# ===========================================================================
# Regex.Variables
# ===========================================================================

class TestRegexVariables:

    def test_extracts_file(self):
        result = Regex.Variables(VARIABLES_HTML)
        assert result["file"] == "As.1001.Posicoes.do.Amor.1978.HDTVRip.x264-gooz.mkv"

    def test_extracts_state(self):
        result = Regex.Variables(VARIABLES_HTML)
        assert result["state"] == "2"

    def test_extracts_position(self):
        result = Regex.Variables(VARIABLES_HTML)
        assert result["position"] == "490945"

    def test_extracts_duration(self):
        result = Regex.Variables(VARIABLES_HTML)
        assert result["duration"] == "4630005"

    def test_extracts_filedir(self):
        result = Regex.Variables(VARIABLES_HTML)
        assert result["filedir"] == "C:\\Users\\allan\\Downloads"

    def test_returns_only_matched_keys(self):
        """Keys not in the pattern (volumelevel, muted, etc.) are excluded."""
        result = Regex.Variables(VARIABLES_HTML)
        assert "volumelevel" not in result
        assert "muted" not in result
        assert "statestring" not in result

    def test_returns_dict(self):
        result = Regex.Variables(VARIABLES_HTML)
        assert isinstance(result, dict)

    def test_empty_html_returns_empty_dict(self):
        assert Regex.Variables("") == {}

    def test_minimal_html_single_tag(self):
        html = '<p id="state">1</p>'
        result = Regex.Variables(html)
        assert result == {"state": "1"}

    def test_matching_is_case_insensitive(self):
        html = '<P ID="state">1</P>'
        result = Regex.Variables(html)
        assert result.get("state") == "1"


# ===========================================================================
# MediaFile.Parse — movies
# ===========================================================================

class TestMediaFileParsemovie:

    def test_parse_returns_media_file_instance(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264.mkv")
        assert isinstance(result, MediaFile)

    def test_movie_title(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264.mkv")
        assert result.title == "Alien"

    def test_movie_type(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264.mkv")
        assert result.type == "movie"

    def test_movie_year(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264.mkv")
        assert result.year == 1979

    def test_movie_screen_size(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264.mkv")
        assert result.screen_size == "1080p"

    def test_movie_container(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264.mkv")
        assert result.container == "mkv"

    def test_movie_video_codec(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264.mkv")
        assert "H.264" in result.video_codec or "x264" in str(result.video_codec)

    def test_movie_without_year_has_no_year_attribute(self):
        result = MediaFile.Parse("Alien.1080p.BluRay.mkv")
        assert not hasattr(result, "year") or result.year is None

    def test_movie_release_group(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264-YIFY.mkv")
        assert result.release_group == "YIFY"

    def test_movie_mimetype(self):
        result = MediaFile.Parse("Alien.1979.1080p.BluRay.x264.mkv")
        assert "video" in result.mimetype


# ===========================================================================
# MediaFile.Parse — series / episodes
# ===========================================================================

class TestMediaFileParseSeries:

    def test_series_title(self):
        result = MediaFile.Parse("Breaking.Bad.S03E07.720p.mkv")
        assert result.title == "Breaking Bad"

    def test_series_type_is_episode(self):
        result = MediaFile.Parse("Breaking.Bad.S03E07.720p.mkv")
        # guessit uses "episode" for individual episodes
        assert result.type == "episode"

    def test_series_season(self):
        result = MediaFile.Parse("Breaking.Bad.S03E07.720p.mkv")
        assert result.season == 3

    def test_series_episode(self):
        result = MediaFile.Parse("Breaking.Bad.S03E07.720p.mkv")
        assert result.episode == 7

    def test_series_screen_size(self):
        result = MediaFile.Parse("Breaking.Bad.S03E07.720p.mkv")
        assert result.screen_size == "720p"

    def test_series_no_year_by_default(self):
        result = MediaFile.Parse("Breaking.Bad.S03E07.720p.mkv")
        assert not hasattr(result, "year") or result.year is None

    def test_series_with_year(self):
        result = MediaFile.Parse("Breaking.Bad.2008.S01E01.mkv")
        assert result.year == 2008

    def test_series_release_group(self):
        result = MediaFile.Parse("Breaking.Bad.S03E07.720p-FLEET.mkv")
        assert result.release_group == "FLEET"


# ===========================================================================
# MediaFile.Parse — attributes are set dynamically
# ===========================================================================

class TestMediaFileParseAttributes:

    def test_unknown_attribute_not_set(self):
        result = MediaFile.Parse("Alien.1979.mkv")
        assert not hasattr(result, "nonexistent_key")

    def test_parse_is_static_method(self):
        # Should be callable without an instance
        result = MediaFile.Parse("Alien.1979.mkv")
        assert result is not None

    def test_multiple_parses_are_independent(self):
        r1 = MediaFile.Parse("Alien.1979.mkv")
        r2 = MediaFile.Parse("Breaking.Bad.S01E01.mkv")
        assert r1.title != r2.title
        assert r1.type != r2.type