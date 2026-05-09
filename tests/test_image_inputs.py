import base64
import tempfile
import unittest
from pathlib import Path

from ai_image_cli.errors import CliError, ExitCode
from ai_image_cli.image_inputs import detect_mime_type, resolve_image_input, validate_single_source

PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+a5WQAAAAASUVORK5CYII="
)


class ImageInputTests(unittest.TestCase):
    def test_validate_single_source_requires_exactly_one(self):
        with self.assertRaises(CliError) as context:
            validate_single_source(file="a.png", url="https://example.com", base64_value=None, stdin_base64=False)
        self.assertEqual(context.exception.exit_code, ExitCode.USAGE)

    def test_detects_png_mime_type(self):
        self.assertEqual(detect_mime_type(PNG_BYTES, explicit_mime_type=None, filename="image.png"), "image/png")

    def test_base64_input_resolves(self):
        payload = resolve_image_input(
            file=None,
            url=None,
            base64_value=base64.b64encode(PNG_BYTES).decode("ascii"),
            stdin_base64=False,
            mime_type=None,
            upload=False,
        )
        self.assertEqual(payload.mime_type, "image/png")
        self.assertEqual(payload.source, "base64")

    def test_stdin_base64_resolves(self):
        payload = resolve_image_input(
            file=None,
            url=None,
            base64_value=None,
            stdin_base64=True,
            mime_type=None,
            upload=False,
            stdin_text=base64.b64encode(PNG_BYTES).decode("ascii"),
        )
        self.assertEqual(payload.source, "stdin")

    def test_file_input_resolves(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "sample.png"
            file_path.write_bytes(PNG_BYTES)
            payload = resolve_image_input(
                file=str(file_path),
                url=None,
                base64_value=None,
                stdin_base64=False,
                mime_type=None,
                upload=False,
            )
        self.assertEqual(payload.file_path, file_path)
