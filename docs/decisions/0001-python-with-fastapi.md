# ADR-0001: Python with FastAPI

- **Status:** Accepted
- **Date:** 2026-11-15

## Context
The service returns the caller's IP and exposes health endpoints. The assignment
mentions flake8, which hints at Python but not at a framework.

## Decision
Python with FastAPI, served by uvicorn.

## Consequences
- Modern framework with a built-in test client and typed request/response models.
- A Python image is larger than a static Go binary; a multi-stage build and a
  minimal base image keep it small (ADR-0020).

## Alternatives considered
- Flask: works, but no typed models or built-in test client.
- Go: smallest image, but less familiar to the author.
- Java / Spring Boot: heavy image and startup for a tiny service.
