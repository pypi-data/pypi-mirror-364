from unittest.mock import patch

import pytest

from sage.config import presets


def test_load_all_creates_defaults(tmp_path):
    """
    Test creation of presets.json if no file exists.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        all_presets = presets.load_all()
        assert "pomodoro" in all_presets
        assert all_presets["pomodoro"] == {"hours": 0, "minutes": 25, "seconds": 0}


def test_create_preset(tmp_path):
    """
    Test creation of preset timer.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        preset = presets.create("workout", "1hr 30m")
        assert preset == {"hours": 1, "minutes": 30, "seconds": 0}

        all_presets = presets.load_all()
        assert "workout" in all_presets
        assert all_presets["workout"] == {"hours": 1, "minutes": 30, "seconds": 0}


def test_preset_getter(tmp_path):
    """
    Test preset getter returns correct time.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        assert presets.get("pomodoro") == {"hours": 0, "minutes": 25, "seconds": 0}


def test_preset_getter_returns_nothing(tmp_path):
    """
    Test preset getter returns nothing for nonexistent preset.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        nothing = presets.get("nothing")
        assert nothing is None


def test_delete_preset(tmp_path):
    """
    Test that a deleted preset is successfully deleted.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        presets.delete("pomodoro")
        assert presets.get("pomodoro") is None


def test_rename_preset(tmp_path):
    """
    Test that a renamed preset is successfully renamed.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        preset = presets.rename("pomodoro", "beans")
        assert preset == {"hours": 0, "minutes": 25, "seconds": 0}
        assert presets.get("beans") == {"hours": 0, "minutes": 25, "seconds": 0}
        assert presets.get("pomodoro") is None


def test_update_preset(tmp_path):
    """
    Test preset duration update.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        preset = presets.update("pomodoro", "30m")
        assert preset == {"hours": 0, "minutes": 30, "seconds": 0}
        assert presets.get("pomodoro") == {"hours": 0, "minutes": 30, "seconds": 0}


def test_preset_create_error_conditions(tmp_path):
    """
    Test various erorr conditions for preset create.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        with pytest.raises(ValueError):
            presets.create("pomodoro", "20 minutes 30 seconds")
        with pytest.raises(ValueError):
            presets.create("bigones", "25 hours")


def test_preset_delete_error_conditions(tmp_path):
    """
    Test various erorr conditions for preset delete.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        with pytest.raises(ValueError):
            presets.delete("nothing")


def test_preset_rename_error_conditions(tmp_path):
    """
    Test various erorr conditions for preset rename.
    """
    presets_file = tmp_path / "presets.json"
    with patch("sage.config.presets.get_json_file", return_value=presets_file):
        with pytest.raises(ValueError):
            presets.rename("nothing", "10 minutes")
