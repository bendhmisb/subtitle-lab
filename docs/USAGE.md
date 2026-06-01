# Usage Guide

This guide shows common `subtitle-lab` workflows.

## Inspect a subtitle file

```bash
python subtitle_lab.py info examples/sample.srt
python subtitle_lab.py info examples/sample.srt --json
```

Use this before editing a subtitle file to confirm the detected format, cue
count, and timeline duration.

## Validate timing

```bash
python subtitle_lab.py validate examples/sample.srt
```

Validation checks for missing cues, invalid time ranges, and overlapping cues.
It exits with a non-zero status when issues are found, so it can be used in CI
jobs or release checks.

## Clean a file

```bash
python subtitle_lab.py clean input.srt -o cleaned.srt
```

Cleaning trims extra whitespace, removes empty cue text, and normalizes SRT cue
numbering.

## Shift timing

```bash
python subtitle_lab.py shift input.srt -o shifted.srt --seconds 1.25
python subtitle_lab.py shift input.srt -o shifted.srt --seconds -0.75
```

Positive values make subtitles appear later. Negative values make subtitles
appear earlier.

## Convert formats

```bash
python subtitle_lab.py convert input.srt -o output.vtt --to vtt
python subtitle_lab.py convert input.vtt -o output.srt --to srt
```

Core conversion is local-only and does not use network services or API keys.
