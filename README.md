# subtitle-lab

Open-source toolkit for cleaning, converting, and syncing subtitle files.

`subtitle-lab` is a small local-first command line tool for common subtitle
maintenance tasks. It does not call any cloud service and does not require an
API key.

## Features

- Convert between `.srt` and `.vtt`
- Shift cue timing forward or backward
- Clean extra whitespace and normalize subtitle numbering
- Run as a single Python file with no third-party dependencies

## Quick start

```bash
python subtitle_lab.py clean examples/sample.srt -o cleaned.srt
python subtitle_lab.py shift examples/sample.srt -o shifted.srt --seconds 1.5
python subtitle_lab.py convert examples/sample.srt -o sample.vtt --to vtt
```

## Install as a CLI

```bash
python -m pip install -e .
subtitle-lab convert examples/sample.srt -o sample.vtt --to vtt
```

## Commands

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
