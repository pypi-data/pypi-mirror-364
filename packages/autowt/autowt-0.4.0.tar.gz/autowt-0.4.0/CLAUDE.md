# Project conventions

Always read @mise.toml.

- Python 3.10+ project using uv for dependency management
- Setup: `mise install && uv sync`
- Format: `mise run format` (ruff)
- Lint: `mise run lint` (ruff)
- Test: `mise run test` (pytest)
- Install pre-commit: `uv run pre-commit install`

## Environment setup

- Create `.env` file with `GITHUB_TOKEN=your_token` for cimonitor
- mise automatically loads .env file (already configured)
- Use `uv run cimonitor status --pr <number>` to check CI status

## Code organization

- `src/autowt/cli.py` - Main CLI entry point with command definitions
- `src/autowt/commands/` - Command implementations (checkout, cleanup, etc.)
- `src/autowt/services/` - Core services (git, state, process management)
- `src/autowt/models/` - Data models and types

## How to get up to speed

- Read README.md

# Workflow

## Updating CHANGELOG.md

When describing a new feature in CHANGELOG.md, avoid multiple sibling bullet points about the same feature. Instead, use a single top-level bullet point per feature, with sub-bullets describing its various aspects.

Readers of the changelog do not care about the sequence of events leading up to a feature's release; they want to read about the feature in one shot.

## The scratchpad directory

ENCOURAGED: Use scratch/ directory for all temporary files or non-documentation Markdown files.
FORBIDDEN: Using /tmp
FORBIDDEN: deleting the entire scratch/ directory

## Docs

For mulit-word doc filenames, smush the words together instead of adding _, -, or spaces between words.
