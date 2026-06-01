# subtitle-lab

Open-source toolkit for cleaning, converting, and syncing subtitle files.

`subtitle-lab` is a small local-first command line tool for common subtitle
maintenance tasks. It does not call any cloud service and does not require an
API key.

## Features

- Convert between `.srt` and `.vtt`
- Shift cue timing forward or backward
- Validate subtitle timing for overlaps and invalid ranges
- Repair overlapping cues and invalid cue durations
- Batch convert subtitle directories while preserving nested folders
- Print subtitle file summaries for quick inspection
- Clean extra whitespace and normalize subtitle numbering
- Run as a single Python file with no third-party dependencies

## Quick start

```bash
python subtitle_lab.py clean examples/sample.srt -o cleaned.srt
python subtitle_lab.py shift examples/sample.srt -o shifted.srt --seconds 1.5
python subtitle_lab.py convert examples/sample.srt -o sample.vtt --to vtt
python subtitle_lab.py validate examples/sample.srt
python subtitle_lab.py repair examples/sample.srt -o repaired.srt --min-gap-ms 100
python subtitle_lab.py batch-convert examples -o converted --to vtt --recursive
python subtitle_lab.py info examples/sample.srt --json
```

## Install as a CLI

```bash
python -m pip install -e .
subtitle-lab convert examples/sample.srt -o sample.vtt --to vtt
```

## Commands

### Inspect subtitles

```bash
python subtitle_lab.py info input.srt
python subtitle_lab.py info input.srt --json
```

This prints the detected format, cue count, start time, end time, and total
timeline duration.

### Validate subtitles

```bash
python subtitle_lab.py validate input.srt
```

This checks that cues are present, each cue ends after it starts, and adjacent
cues do not overlap.

### Repair timing

```bash
python subtitle_lab.py repair input.srt -o repaired.srt --min-gap-ms 100
```

This sorts cues by time, moves overlapping cues after the previous cue, and
extends invalid cue durations. Use `--min-duration-ms` to control the fallback
duration for cues whose end time is not after the start time.

### Batch convert subtitles

```bash
python subtitle_lab.py batch-convert input_dir -o output_dir --to vtt --recursive
```

This scans a directory for `.srt` and `.vtt` files, converts each file to the
target format, and preserves nested folder structure in the output directory.

### Clean subtitles

```bash
python subtitle_lab.py clean input.srt -o output.srt
```

This trims whitespace, removes empty cues, normalizes cue numbering, and keeps
the original subtitle format unless `--to` is provided.

### Shift timing

```bash
python subtitle_lab.py shift input.srt -o output.srt --seconds -0.75
```

Positive values move subtitles later. Negative values move subtitles earlier.
Timestamps are clamped at zero.

### Convert formats

```bash
python subtitle_lab.py convert input.vtt -o output.srt --to srt
python subtitle_lab.py convert input.srt -o output.vtt --to vtt
```

## Development

```bash
python -m unittest discover -s tests
```

## Security

This project is designed to run locally and does not need secrets. Do not commit
`.env` files, API keys, tokens, or private subtitle files. The included
`.gitignore` excludes common secret and local environment files.

## License

MIT
