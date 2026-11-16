"""AI diagnosis of failed CI runs (ADR-0005, ADR-0027).

Runs as the last CI job, only when an earlier job failed. Reads the failed
jobs' logs, asks a language model for a structured diagnosis, and posts it as
one sticky PR comment and in the run summary.

Logs are untrusted input. The job never executes anything from the logs or
the model's answer, only publishes sanitized text, and its only secret is
AI_API_KEY, the model provider's API key.
"""
