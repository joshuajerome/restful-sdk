# Branching Guide

restful follows the same branching model as CUTIP.

## Branches

| Branch | Purpose | Push directly? |
|--------|---------|---------------|
| `integration` | Stable, deploys docs to GitHub Pages | Never — merge from staging |
| `staging` | Development target | Never — merge from feat/bug branches |
| `feat/cap{N}-slug` | New feature | Yes |
| `bug/cap{N}-slug` | Bug fix | Yes |
| `docs/slug` | Documentation update | Yes |
| `release/vX.Y.Z` | Release branch (triggers CI) | Created from integration |

## Flow

```
feat/cap001-typed-endpoints
    └→ PR → staging
                └→ merge → integration
                                └→ release/v0.1.0
```

## Capability IDs

Every feature or bug fix gets a sequential `cap{N}` ID:

- Format: `cap001`, `cap002`, ... (zero-padded, 3 digits)
- Assigned at branch creation, never reused
- Used in: branch name, commit prefix, PR title

## Commit Messages

```
[cap001] feat: add typed endpoint generation
[cap002] fix: handle duplicate endpoint names
```

## PR Requirements

Every PR must include:
- `--assignee joshuajerome`
- `--label {feature|bugfix|documentation|automation}`
- Body from `.claude/templates/pr-body.md`
