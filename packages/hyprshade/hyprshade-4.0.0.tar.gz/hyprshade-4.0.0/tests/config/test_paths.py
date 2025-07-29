import re
from pathlib import Path

import pytest

from hyprshade.config import utils


class TestXDG:
    def test_uses_xdg_config_home(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        assert utils.xdg_config_home() == str(tmp_path)

    def test_uses_home(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setenv("HOME", str(tmp_path))
        assert utils.xdg_config_home() == str(tmp_path / ".config")

    def test_raises_when_cannot_be_determined(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.delenv("HOME", raising=False)
        with pytest.raises(
            ValueError, match=re.escape("$HOME environment variable is not set")
        ):
            utils.xdg_config_home()


class TestConfigHomes:
    def test_hypr(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        assert utils.hypr_config_home() == str(tmp_path / "hypr")

    def test_hyprshade(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        assert utils.hyprshade_config_home() == str(tmp_path / "hyprshade")

    def test_systemd_user(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        assert utils.systemd_user_config_home() == str(tmp_path / "systemd/user")
