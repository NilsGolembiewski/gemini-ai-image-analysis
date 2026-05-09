import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai_image_cli.config import get_api_key_cache_path, resolve_api_key, save_api_key
from ai_image_cli.errors import CliError, ExitCode


class ResolveApiKeyTests(unittest.TestCase):
    def test_prefers_explicit_api_key(self):
        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "env-key"}, clear=True):
            self.assertEqual(resolve_api_key(explicit_api_key="cli-key", dotenv_path=None), "cli-key")

    def test_uses_existing_environment_before_dotenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text("GEMINI_IMAGE_CLI_GOOGLE_API_KEY=dotenv-key\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"GOOGLE_API_KEY": "env-key"}, clear=True):
                self.assertEqual(resolve_api_key(explicit_api_key=None, dotenv_path=dotenv_path), "env-key")

    def test_loads_custom_repo_key_from_dotenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text("GEMINI_IMAGE_CLI_GOOGLE_API_KEY=dotenv-key\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {}, clear=True):
                self.assertEqual(resolve_api_key(explicit_api_key=None, dotenv_path=dotenv_path), "dotenv-key")

    def test_uses_cached_key_before_dotenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text("GEMINI_IMAGE_CLI_GOOGLE_API_KEY=dotenv-key\n", encoding="utf-8")
            with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": temp_dir}, clear=True):
                save_api_key("cached-key")
                self.assertEqual(resolve_api_key(explicit_api_key=None, dotenv_path=dotenv_path), "cached-key")

    def test_environment_still_beats_cached_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": temp_dir, "GOOGLE_API_KEY": "env-key"}, clear=True):
                save_api_key("cached-key")
                self.assertEqual(resolve_api_key(explicit_api_key=None, dotenv_path=None), "env-key")

    def test_blank_environment_value_does_not_block_cached_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": temp_dir, "GOOGLE_API_KEY": "   "}, clear=True):
                save_api_key("cached-key")
                self.assertEqual(resolve_api_key(explicit_api_key=None, dotenv_path=None), "cached-key")

    def test_save_api_key_uses_private_permissions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": temp_dir}, clear=True):
                cache_path = save_api_key("cached-key")
                self.assertEqual(cache_path, get_api_key_cache_path())
                self.assertEqual(cache_path.read_text(encoding="utf-8"), "cached-key\n")
                self.assertEqual(stat.S_IMODE(cache_path.parent.stat().st_mode), 0o700)
                self.assertEqual(stat.S_IMODE(cache_path.stat().st_mode), 0o600)

    def test_raises_when_no_key_exists(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CliError) as context:
                resolve_api_key(explicit_api_key=None, dotenv_path=None)
        self.assertEqual(context.exception.exit_code, ExitCode.AUTH)

    def test_raises_when_explicit_api_key_is_empty(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CliError) as context:
                resolve_api_key(explicit_api_key="   ", dotenv_path=None)
        self.assertEqual(context.exception.exit_code, ExitCode.AUTH)

    def test_raises_when_cached_key_is_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": temp_dir}, clear=True):
                cache_path = get_api_key_cache_path()
                cache_path.parent.mkdir(parents=True)
                cache_path.write_text("\n", encoding="utf-8")

                with self.assertRaises(CliError) as context:
                    resolve_api_key(explicit_api_key=None, dotenv_path=None)

        self.assertEqual(context.exception.exit_code, ExitCode.AUTH)
