import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai_image_cli.config import resolve_api_key
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

    def test_raises_when_no_key_exists(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(CliError) as context:
                resolve_api_key(explicit_api_key=None, dotenv_path=None)
        self.assertEqual(context.exception.exit_code, ExitCode.AUTH)
