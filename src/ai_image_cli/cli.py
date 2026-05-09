from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_image_cli import __version__
from ai_image_cli.config import resolve_api_key, save_api_key
from ai_image_cli.errors import CliError, ExitCode
from ai_image_cli.formatters import normalize_json_output, write_output
from ai_image_cli.gemini_client import analyze_with_gemini
from ai_image_cli.image_inputs import resolve_image_input
from ai_image_cli.models import AnalysisRequest
from ai_image_cli.prompts import (
    GENERIC_ANALYZE_JSON_SCHEMA,
    MOBILE_JSON_SCHEMA,
    WEBPAGE_JSON_SCHEMA,
    build_analyze_prompt,
    build_mobile_prompt,
    build_webpage_prompt,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ai-image-cli", description="Analyze images with Gemini 3 Flash.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--auth",
        action="store_true",
        help="Cache the Gemini API key from --api-key or stdin, then exit.",
    )
    parser.add_argument("--api-key")
    parser.add_argument("--dotenv-path", default=".env")

    common = argparse.ArgumentParser(add_help=False)
    source_group = common.add_mutually_exclusive_group(required=True)
    source_group.add_argument("--file")
    source_group.add_argument("--url")
    source_group.add_argument("--base64")
    source_group.add_argument("--stdin-base64", action="store_true")
    prompt_group = common.add_mutually_exclusive_group()
    prompt_group.add_argument("--prompt")
    prompt_group.add_argument("--prompt-file")
    common.add_argument("--mime-type")
    common.add_argument("--api-key")
    common.add_argument("--dotenv-path", default=".env")
    common.add_argument("--output")
    common.add_argument("--upload", action="store_true")
    common.add_argument("--max-output-tokens", type=int)
    common.add_argument("--verbose", action="store_true")
    common.add_argument("--quiet", action="store_true")

    subparsers = parser.add_subparsers(dest="command")

    analyze = subparsers.add_parser("analyze", aliases=["image"], parents=[common], help="Analyze a general image.")
    analyze.add_argument("--format", choices=("text", "json"), default="text")
    analyze.add_argument("--temperature", type=float)

    webpage = subparsers.add_parser(
        "analyze-webpage",
        aliases=["webpage"],
        parents=[common],
        help="Analyze a webpage screenshot.",
    )
    webpage.add_argument("--format", choices=("text", "json"), default="json")
    webpage.add_argument(
        "--focus",
        choices=("layout", "content", "navigation", "forms", "interactive", "accessibility"),
    )
    webpage.add_argument("--include-accessibility", action=argparse.BooleanOptionalAction, default=True)

    mobile = subparsers.add_parser(
        "analyze-mobile",
        aliases=["mobile"],
        parents=[common],
        help="Analyze a mobile app screenshot.",
    )
    mobile.add_argument("--format", choices=("text", "json"), default="json")
    mobile.add_argument("--platform", choices=("ios", "android", "auto"), default="auto")
    mobile.add_argument(
        "--focus",
        choices=("ui-design", "user-experience", "navigation", "accessibility", "performance", "onboarding"),
    )
    mobile.add_argument("--include-ux-heuristics", action=argparse.BooleanOptionalAction, default=True)

    return parser


def _read_prompt(args: argparse.Namespace) -> str | None:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    return args.prompt


def _emit_error(message: str, *, stderr, quiet: bool) -> None:
    if not quiet:
        stderr.write(message.rstrip() + "\n")


def _read_auth_api_key(args: argparse.Namespace, stdin_text: str | None) -> str:
    if args.api_key is not None:
        return args.api_key

    if stdin_text is not None:
        return stdin_text.strip()

    return sys.stdin.read().strip()


def _build_request(args: argparse.Namespace, prompt: str | None) -> tuple[AnalysisRequest, dict | None]:
    if args.command in {"analyze", "image"}:
        return (
            AnalysisRequest(
                command="analyze",
                prompt=build_analyze_prompt(prompt),
                output_format=args.format,
                max_output_tokens=args.max_output_tokens,
                temperature=args.temperature,
                upload=args.upload,
            ),
            GENERIC_ANALYZE_JSON_SCHEMA if args.format == "json" else None,
        )
    if args.command in {"analyze-webpage", "webpage"}:
        return (
            AnalysisRequest(
                command="analyze-webpage",
                prompt=build_webpage_prompt(
                    focus=args.focus,
                    include_accessibility=args.include_accessibility,
                    user_prompt=prompt,
                ),
                output_format=args.format,
                max_output_tokens=args.max_output_tokens,
                upload=args.upload,
            ),
            WEBPAGE_JSON_SCHEMA if args.format == "json" else None,
        )
    return (
        AnalysisRequest(
            command="analyze-mobile",
            prompt=build_mobile_prompt(
                platform=args.platform,
                focus=args.focus,
                include_ux_heuristics=args.include_ux_heuristics,
                user_prompt=prompt,
            ),
            output_format=args.format,
            max_output_tokens=args.max_output_tokens,
            upload=args.upload,
        ),
        MOBILE_JSON_SCHEMA if args.format == "json" else None,
    )


def main(argv: list[str] | None = None, *, stdout=None, stderr=None, stdin_text: str | None = None) -> int:
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr
    parser = build_parser()
    args: argparse.Namespace | None = None

    try:
        args = parser.parse_args(argv)
        if args.auth:
            if args.command is not None:
                raise CliError("Use --auth without a subcommand.", ExitCode.USAGE)
            save_api_key(_read_auth_api_key(args, stdin_text))
            return ExitCode.SUCCESS
        if args.command is None:
            raise CliError("A command is required unless --auth is used.", ExitCode.USAGE)
        if args.verbose and args.quiet:
            raise CliError("Choose either --verbose or --quiet, not both.", ExitCode.USAGE)

        prompt = _read_prompt(args)
        request, response_schema = _build_request(args, prompt)
        api_key = resolve_api_key(explicit_api_key=args.api_key, dotenv_path=args.dotenv_path)
        image = resolve_image_input(
            file=args.file,
            url=args.url,
            base64_value=args.base64,
            stdin_base64=args.stdin_base64,
            mime_type=args.mime_type,
            upload=args.upload,
            stdin_text=stdin_text,
        )
        raw_output = analyze_with_gemini(
            api_key=api_key,
            image=image,
            request=request,
            response_schema=response_schema,
        )
        final_output = normalize_json_output(raw_output) if request.output_format == "json" else raw_output
        write_output(final_output, Path(args.output) if args.output else None)
        if not args.output:
            stdout.write(final_output)
            if not final_output.endswith("\n"):
                stdout.write("\n")
        return ExitCode.SUCCESS
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else ExitCode.USAGE
        return code
    except KeyboardInterrupt:
        _emit_error("Interrupted.", stderr=stderr, quiet=False)
        return ExitCode.TIMEOUT
    except CliError as exc:
        detail_suffix = f" ({exc.details})" if exc.details and getattr(args, "verbose", False) else ""
        quiet = getattr(args, "quiet", False) and exc.exit_code != ExitCode.USAGE
        _emit_error(f"Error: {exc.message}{detail_suffix}", stderr=stderr, quiet=quiet)
        return exc.exit_code
    except FileNotFoundError as exc:
        _emit_error(f"Error: {exc}", stderr=stderr, quiet=getattr(args, "quiet", False))
        return ExitCode.INPUT
