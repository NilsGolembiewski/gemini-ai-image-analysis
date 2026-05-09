import io
import json
import unittest
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
