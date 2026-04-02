# CI/CD Workflows

## CI (`ci.yml`)

Runs on every push to `feat/**`, `bug/**`, `claude/**` branches and PRs to staging/integration.

**Jobs:**
- **Auto-label** — derives label from branch prefix, assigns to PR author
- **Ruff Lint** — `ruff check .`
- **Ruff Format** — `ruff format --check .`
- **Type Check** — `ty check`
- **Unit Tests** — `pytest tests/ -v`

## Docs (`docs.yml`)

Runs on PRs touching `docs/**` or `mkdocs.yml`, and pushes to staging/integration.

**Jobs:**
- **Build** — `mkdocs build --strict` (fails on warnings)
- **Deploy** — `mkdocs gh-deploy --force` (integration push only)

## Release (`release.yml`)

Runs when a `release/*` branch is pushed.

**Jobs:**
- Unit tests
- Smoke test (build wheel, install, import check)
- GitHub Release with wheel asset

See [Release Process](#) for the full playbook.
