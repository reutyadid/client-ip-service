# ADR-0017: CLAUDE.md for AI-assisted development

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
- `CLAUDE.md`, in English, holds only project facts the assistant cannot infer
  from the code: commands, layout, conventions, pitfalls. It stays short and
  lists only commands that exist and were checked.
- Personal working preferences go in `CLAUDE.local.md`, which is git-ignored.
- Rules that must never be broken are enforced by configuration, not text:
  `.claude/settings.json` denies `git commit` and `git push`.
