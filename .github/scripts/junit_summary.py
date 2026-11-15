"""Turn a pytest JUnit XML report into Markdown for the GitHub run summary.

Usage, in a workflow step that runs even when tests fail:

    python3 .github/scripts/junit_summary.py "Unit tests" report.xml \
        >> "$GITHUB_STEP_SUMMARY"

Standard library only, so it runs on any runner without installing anything.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def outcome(case: ET.Element) -> str:
    if case.find("failure") is not None or case.find("error") is not None:
        return "failed"
    if case.find("skipped") is not None:
        return "skipped"
    return "passed"


ICONS = {"passed": "✅", "failed": "❌", "skipped": "⏭️"}


def main() -> None:
    title, report = sys.argv[1], Path(sys.argv[2])
    print(f"## {title}")

    # pytest may crash before writing the report; say so instead of failing here
    if not report.exists():
        print(f"\n⚠️ No report found at `{report}`. Check the test step's log.")
        return

    # S314 warns about parsing untrusted XML. This report was written by pytest
    # in the same job, so it is trusted input.
    cases = list(ET.parse(report).getroot().iter("testcase"))  # noqa: S314
    results = [(outcome(c), f"{c.get('classname')}::{c.get('name')}") for c in cases]
    counts = {key: sum(1 for o, _ in results if o == key) for key in ICONS}

    print("\n" + " · ".join(f"{ICONS[k]} {counts[k]} {k}" for k in ICONS))

    # Failures first and always visible: they are why someone opens the summary
    failed = [name for o, name in results if o == "failed"]
    if failed:
        print("\n### Failed")
        for name in failed:
            print(f"- ❌ `{name}`")

    # The full list stays collapsed so a long suite does not bury the rest
    print(f"\n<details><summary>All {len(results)} tests</summary>\n")
    for o, name in results:
        print(f"- {ICONS[o]} `{name}`")
    print("\n</details>")


if __name__ == "__main__":
    main()
