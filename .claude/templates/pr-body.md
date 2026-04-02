# PR Body Templates

Copy the section matching your branch type. Fill every `{placeholder}`.
Write the filled body to `/tmp/pr-body.md` and pass `--body-file /tmp/pr-body.md` to `gh pr create`.

**Every PR must include:**
- `--assignee joshuajerome` — always
- `--label {feat|bug|docs|gh|claude}` — always, matching the branch type

---

## feat/cap{N} — New Feature

```markdown
## Summary

- {one sentence: what new capability this adds}
- {implementation approach in 1–2 sentences}
- {any trade-offs or known limitations}

## Changes

- `{file}`: {what changed and why}
- `{file}`: {what changed and why}

## Test plan

- [ ] `uv run pytest tests/ -v` passes
- [ ] {feature-specific manual test step}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## bug/cap{N} — Bug Fix

```markdown
## Summary

**Root cause:** {one sentence — what code path caused the failure}

**Fix:** {what changed and why it resolves the root cause}

Closes #{issue-number}

## Changes

- `{file}:{line}`: {what changed}
- `{file}:{line}`: {what changed}

## Test plan

- [ ] `uv run pytest tests/ -v` passes
- [ ] Reproduction steps from the issue no longer reproduce
- [ ] {any regression test added}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## docs/cap{N} — Documentation

```markdown
## Summary

Auto-generated patch notes and capability registry entry for `{source-branch}`.

## Changes

- `docs/capabilities.md`: added `{cap{N}}` entry
- `docs/patch-notes.md`: added patch note for `{cap{N}}`

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## gh/* — GitHub Actions Change

```markdown
## Summary

- {what the workflow or script change does}
- {why it was needed / what problem it solves}

## Changes

- `.github/workflows/{file}`: {what changed}

## Test plan

- [ ] Workflow YAML has no syntax errors
- [ ] Trigger condition is correct for intended events

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

---

## bump: version — Release Version Bump

```markdown
## Summary

Version bump for the {X.Y.Z} release.

- `pyproject.toml`: `{A.B.C}` → `{X.Y.Z}`
- `docs/patch-notes.md`: added v{X.Y.Z} release section

## Caps shipping in this release

{List cap IDs and titles from docs/capabilities.md that are shipping}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```
