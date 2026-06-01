# Contributing

Thanks for helping improve `subtitle-lab`.

## Local setup

```bash
python -m pip install -e .
python -m unittest discover -s tests
```

## Useful contribution areas

- More subtitle format fixtures
- Better handling for malformed SRT/VTT files
- Timecode validation and repair suggestions
- Documentation examples for creator workflows
- Packaging and release automation

## Pull request checklist

- Keep the tool local-first and dependency-light.
- Add or update tests for behavior changes.
- Do not commit private subtitle files, `.env` files, credentials, or API keys.
- Run `python -m unittest discover -s tests` before opening a pull request.
