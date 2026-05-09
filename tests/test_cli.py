import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ai_image_cli import cli
from ai_image_cli.errors import ExitCode


class CliTests(unittest.TestCase):
    def test_json_command_prints_only_json(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch("ai_image_cli.cli.resolve_api_key", return_value="key"), mock.patch(
            "ai_image_cli.cli.resolve_image_input", return_value=object()
        ), mock.patch(
            "ai_image_cli.cli.analyze_with_gemini",
            return_value='{"summary":"ok","detected_text":[],"key_elements":[],"notable_details":[],"confidence_notes":"high"}',
        ):
            exit_code = cli.main(["analyze", "--base64", "aGVsbG8=", "--format", "json"], stdout=stdout, stderr=stderr)
        self.assertEqual(exit_code, ExitCode.SUCCESS)
        self.assertEqual(stderr.getvalue(), "")
        parsed = json.loads(stdout.getvalue())
        self.assertEqual(parsed["summary"], "ok")

    def test_prompt_file_is_used(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch("pathlib.Path.read_text", return_value="from file"), mock.patch(
            "ai_image_cli.cli.resolve_api_key", return_value="key"
        ), mock.patch("ai_image_cli.cli.resolve_image_input", return_value=object()), mock.patch(
            "ai_image_cli.cli.analyze_with_gemini", return_value="done"
        ) as analyze_mock:
            exit_code = cli.main(["analyze", "--base64", "aGVsbG8=", "--prompt-file", "prompt.txt"], stdout=stdout, stderr=stderr)
        self.assertEqual(exit_code, ExitCode.SUCCESS)
        request = analyze_mock.call_args.kwargs["request"]
        self.assertEqual(request.prompt, "from file")

    def test_conflicting_logging_flags_fail(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        exit_code = cli.main(["analyze", "--base64", "aGVsbG8=", "--verbose", "--quiet"], stdout=stdout, stderr=stderr)
        self.assertEqual(exit_code, ExitCode.USAGE)
        self.assertIn("Choose either --verbose or --quiet", stderr.getvalue())

    def test_auth_caches_api_key_from_flag(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.dict("os.environ", {"XDG_CONFIG_HOME": temp_dir}, clear=True):
            exit_code = cli.main(["--auth", "--api-key", "flag-key"], stdout=stdout, stderr=stderr)
            cache_path = Path(temp_dir) / "ai-image-cli" / "google-api-key"
            cached_value = cache_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, ExitCode.SUCCESS)
        self.assertEqual(stderr.getvalue(), "")
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(cached_value, "flag-key\n")

    def test_auth_caches_api_key_from_stdin(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.dict("os.environ", {"XDG_CONFIG_HOME": temp_dir}, clear=True):
            exit_code = cli.main(["--auth"], stdout=stdout, stderr=stderr, stdin_text="stdin-key\n")
            cache_path = Path(temp_dir) / "ai-image-cli" / "google-api-key"
            cached_value = cache_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, ExitCode.SUCCESS)
        self.assertEqual(cached_value, "stdin-key\n")

    def test_auth_rejects_subcommands(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = cli.main(["--auth", "analyze", "--base64", "aGVsbG8="], stdout=stdout, stderr=stderr)

        self.assertEqual(exit_code, ExitCode.USAGE)
        self.assertIn("Use --auth without a subcommand.", stderr.getvalue())

    def test_auth_empty_api_key_does_not_fall_back_to_stdin(self):
        stdout = io.StringIO()
        stderr = io.StringIO()

        exit_code = cli.main(["--auth", "--api-key", "   "], stdout=stdout, stderr=stderr, stdin_text="stdin-key\n")

        self.assertEqual(exit_code, ExitCode.AUTH)
        self.assertIn("No Gemini API key provided for --auth.", stderr.getvalue())

    def test_normal_command_uses_cached_key(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.dict("os.environ", {"XDG_CONFIG_HOME": temp_dir}, clear=True), mock.patch(
            "ai_image_cli.cli.resolve_image_input", return_value=object()
        ), mock.patch("ai_image_cli.cli.analyze_with_gemini", return_value="done") as analyze_mock:
            cache_dir = Path(temp_dir) / "ai-image-cli"
            cache_dir.mkdir()
            (cache_dir / "google-api-key").write_text("cached-key\n", encoding="utf-8")

            exit_code = cli.main(["analyze", "--base64", "aGVsbG8="], stdout=stdout, stderr=stderr)

        self.assertEqual(exit_code, ExitCode.SUCCESS)
        self.assertEqual(analyze_mock.call_args.kwargs["api_key"], "cached-key")
