"""AI diagnosis of failed CI runs (decisions 5, 6, 24).

Runs as the last CI job, only when an earlier job failed. Reads the failed
jobs' logs, asks a language model for a structured diagnosis, and posts it as
one sticky PR comment and in the run summary.

Logs are untrusted input. The job holds no repository secrets, never executes
anything from the logs or the model's answer, and only publishes sanitized text.
"""
