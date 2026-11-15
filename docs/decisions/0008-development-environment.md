# ADR-0008: Development environment

- **Status:** Accepted
- **Date:** 2026-11-15

## Decision
Development, the kind cluster and the self-hosted runner all run locally on
Windows with WSL2 and Docker Desktop. Claude Code is used as a coding
assistant; it is blocked from committing or pushing (`.claude/settings.json`),
so every commit is made and reviewed by the author.
