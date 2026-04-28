from __future__ import annotations

import argparse
import os
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTENT_DIR = REPO_ROOT / "content"
DEFAULT_THRESHOLD_BYTES = 500_000


def format_size(size: int) -> str:
    return f"{size / 1_000_000:.2f} MB"


def build_report(threshold: int) -> str:
    image_paths = sorted(
        [
            path
            for path in CONTENT_DIR.glob("*")
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp", ".gif"}
        ],
        key=lambda path: path.stat().st_size,
        reverse=True,
    )
    oversized = [
        (path, path.stat().st_size)
        for path in image_paths
        if path.stat().st_size > threshold
    ]

    lines = [
        "## Image size report",
        "",
        f"Threshold: {format_size(threshold)}",
        "",
    ]

    if not oversized:
        lines.append("No images exceed the threshold.")
        return "\n".join(lines)

    lines.extend(["| Image | Size |", "| --- | ---: |"])

    for path, size in oversized:
        relative = path.relative_to(REPO_ROOT).as_posix()
        lines.append(f"| `{relative}` | {format_size(size)} |")

    lines.extend(
        [
            "",
            "This report is informational only; it does not fail the workflow.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Report oversized content images without failing.")
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD_BYTES)
    args = parser.parse_args()
    report = build_report(args.threshold)
    print(report)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")

    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary_file:
            summary_file.write(report)
            summary_file.write("\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
