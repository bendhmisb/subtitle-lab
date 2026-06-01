"""A small local-first CLI for cleaning, shifting, and converting subtitles."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Iterable


SRT_TIME_RE = re.compile(
    r"(?P<start>\d{1,2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*"
    r"(?P<end>\d{1,2}:\d{2}:\d{2}[,.]\d{3})(?P<settings>.*)"
)


@dataclass
class Cue:
    start_ms: int
    end_ms: int
    lines: list[str]
    settings: str = ""


def parse_timestamp(value: str) -> int:
    hours, minutes, rest = value.replace(",", ".").split(":")
    seconds, millis = rest.split(".")
    return (
        int(hours) * 3_600_000
        + int(minutes) * 60_000
        + int(seconds) * 1_000
        + int(millis[:3].ljust(3, "0"))
    )


def format_timestamp(ms: int, *, style: str) -> str:
    ms = max(0, int(ms))
    hours, remainder = divmod(ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, millis = divmod(remainder, 1_000)
    separator = "," if style == "srt" else "."
    return f"{hours:02}:{minutes:02}:{seconds:02}{separator}{millis:03}"


def detect_format(path: Path, text: str) -> str:
    if path.suffix.lower() == ".vtt" or text.lstrip().startswith("WEBVTT"):
        return "vtt"
    return "srt"


def clean_text_lines(lines: Iterable[str]) -> list[str]:
    cleaned: list[str] = []
    for line in lines:
        normalized = re.sub(r"[ \t]+", " ", line.strip())
        if normalized:
            cleaned.append(normalized)
    return cleaned


def parse_subtitles(text: str) -> list[Cue]:
    text = text.replace("\ufeff", "").replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"^\s*WEBVTT[^\n]*\n+", "", text, flags=re.IGNORECASE)
    chunks = re.split(r"\n{2,}", text.strip())
    cues: list[Cue] = []

    for chunk in chunks:
        lines = [line.rstrip() for line in chunk.split("\n") if line.strip()]
        if not lines:
            continue

        time_index = next((i for i, line in enumerate(lines) if "-->" in line), -1)
        if time_index < 0:
            continue

        match = SRT_TIME_RE.search(lines[time_index])
        if not match:
            continue

        body = clean_text_lines(lines[time_index + 1 :])
        if not body:
            continue

        cues.append(
            Cue(
                start_ms=parse_timestamp(match.group("start")),
                end_ms=parse_timestamp(match.group("end")),
                settings=match.group("settings").strip(),
                lines=body,
            )
        )

    return cues


def shift_cues(cues: Iterable[Cue], offset_ms: int) -> list[Cue]:
    shifted: list[Cue] = []
    for cue in cues:
        shifted.append(
            Cue(
                start_ms=max(0, cue.start_ms + offset_ms),
                end_ms=max(0, cue.end_ms + offset_ms),
                settings=cue.settings,
                lines=list(cue.lines),
            )
        )
    return shifted


def validate_cues(cues: list[Cue]) -> list[str]:
    issues: list[str] = []
    if not cues:
        return ["No valid subtitle cues were found."]

    previous_end = 0
    for index, cue in enumerate(cues, start=1):
        if cue.end_ms <= cue.start_ms:
            issues.append(f"Cue {index}: end time must be after start time.")
        if cue.start_ms < previous_end:
            issues.append(f"Cue {index}: overlaps with the previous cue.")
        if not cue.lines:
            issues.append(f"Cue {index}: cue text is empty.")
        previous_end = max(previous_end, cue.end_ms)

    return issues


def render_srt(cues: Iterable[Cue]) -> str:
    blocks: list[str] = []
    for index, cue in enumerate(cues, start=1):
        blocks.append(
            "\n".join(
                [
                    str(index),
                    f"{format_timestamp(cue.start_ms, style='srt')} --> "
                    f"{format_timestamp(cue.end_ms, style='srt')}",
                    *cue.lines,
                ]
            )
        )
    return "\n\n".join(blocks) + "\n"


def render_vtt(cues: Iterable[Cue]) -> str:
    blocks = ["WEBVTT", ""]
    for cue in cues:
        settings = f" {cue.settings}" if cue.settings else ""
        blocks.append(
            "\n".join(
                [
                    f"{format_timestamp(cue.start_ms, style='vtt')} --> "
                    f"{format_timestamp(cue.end_ms, style='vtt')}{settings}",
                    *cue.lines,
                ]
            )
        )
        blocks.append("")
    return "\n".join(blocks).rstrip() + "\n"


def load_cues(path: Path) -> tuple[list[Cue], str]:
    text = path.read_text(encoding="utf-8")
    return parse_subtitles(text), detect_format(path, text)


def write_cues(path: Path, cues: list[Cue], output_format: str) -> None:
    rendered = render_vtt(cues) if output_format == "vtt" else render_srt(cues)
    path.write_text(rendered, encoding="utf-8")


def command_clean(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    cues, source_format = load_cues(input_path)
    output_format = args.to or source_format
    write_cues(Path(args.output), cues, output_format)


def command_shift(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    cues, source_format = load_cues(input_path)
    output_format = args.to or source_format
    write_cues(Path(args.output), shift_cues(cues, int(args.seconds * 1000)), output_format)


def command_convert(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    cues, _source_format = load_cues(input_path)
    write_cues(Path(args.output), cues, args.to)


def command_validate(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    cues, _source_format = load_cues(input_path)
    issues = validate_cues(cues)

    if issues:
        for issue in issues:
            print(f"ERROR: {issue}", file=sys.stderr)
        raise SystemExit(1)

    print(f"OK: {len(cues)} subtitle cue(s) passed validation.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Clean, shift, and convert subtitles.")
    subparsers = parser.add_subparsers(required=True)

    clean = subparsers.add_parser("clean", help="Clean whitespace and numbering.")
    clean.add_argument("input")
    clean.add_argument("-o", "--output", required=True)
    clean.add_argument("--to", choices=("srt", "vtt"), help="Optional output format.")
    clean.set_defaults(func=command_clean)

    shift = subparsers.add_parser("shift", help="Shift cue timestamps.")
    shift.add_argument("input")
    shift.add_argument("-o", "--output", required=True)
    shift.add_argument("--seconds", type=float, required=True)
    shift.add_argument("--to", choices=("srt", "vtt"), help="Optional output format.")
    shift.set_defaults(func=command_shift)

    convert = subparsers.add_parser("convert", help="Convert subtitle format.")
    convert.add_argument("input")
    convert.add_argument("-o", "--output", required=True)
    convert.add_argument("--to", choices=("srt", "vtt"), required=True)
    convert.set_defaults(func=command_convert)

    validate = subparsers.add_parser("validate", help="Validate subtitle timing.")
    validate.add_argument("input")
    validate.set_defaults(func=command_validate)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
