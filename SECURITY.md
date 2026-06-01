# Security Policy

## Reporting a vulnerability

Please open a GitHub issue if you find a security concern in `subtitle-lab`.
Avoid posting private subtitle files, API keys, tokens, or credentials in the
issue body.

## Project security model

`subtitle-lab` is designed to run locally. It does not require cloud services,
network access, or API keys for core functionality.

Areas that deserve careful review:

- Parsing malformed subtitle files
- File path handling
- Release packaging
- GitHub Actions workflow changes

## Secret handling

The repository should not contain secrets. `.gitignore` excludes common local
environment and credential files, including `.env`, key files, and credential
files.
