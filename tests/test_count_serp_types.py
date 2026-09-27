"""Tests for skills/blog-brief/scripts/count_serp_types.py.

The script reads the organic results table in `serp-intent.md`, counts rows
per page type, and fills the `## Page type counts` section with the counts,
the core intent page type, and the continue/stop decision (K-015).

Stdlib + pytest only. No network. Subprocess invocation matches the
documented CLI.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "blog-brief"
    / "scripts"
    / "count_serp_types.py"
)


def _serp_intent_file(tmp_path: Path, result_rows: list[tuple[str, str, str]]) -> Path:
    table_lines = [
        "| Rank | URL | Title | Page type |",
        "|---|---|---|---|",
    ]
    for rank_number, (url, title, page_type) in enumerate(result_rows, start=1):
        table_lines.append(f"| {rank_number} | {url} | {title} | {page_type} |")
    serp_intent_text = "\n".join(
        [
            "# SERP intent: test keyword",
            "",
            "- Focus keyword: test keyword",
            "",
            "## Top 10 organic results",
            "",
            *table_lines,
            "",
            "## Page type counts",
            "",
            "## AI Overview",
            "",
            "Present: no",
            "",
        ]
    )
    serp_intent_path = tmp_path / "serp-intent.md"
    serp_intent_path.write_text(serp_intent_text, encoding="utf-8")
    return serp_intent_path


def _run(serp_intent_path: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(serp_intent_path)],
        capture_output=True,
        text=True,
    )


def _counts_section(serp_intent_path: Path) -> str:
    serp_intent_text = serp_intent_path.read_text(encoding="utf-8")
    section_start = serp_intent_text.index("## Page type counts")
    section_end = serp_intent_text.index("## AI Overview")
    return serp_intent_text[section_start:section_end]


def test_blog_majority_fills_counts_and_continues(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [
            ("https://a.com/post", "Post A", "blog/guide"),
            ("https://b.com/post", "Post B", "blog/guide"),
            ("https://shop.com/c/men", "Men's Costumes", "category"),
            ("https://www.youtube.com/watch?v=1", "Video", "other: video"),
        ],
    )

    completed = _run(serp_intent_path)

    assert completed.returncode == 0, completed.stderr
    counts_section = _counts_section(serp_intent_path)
    assert "| blog/guide | 2 |" in counts_section
    assert "| category | 1 |" in counts_section
    assert "| product | 0 |" in counts_section
    assert "| other | 1 |" in counts_section
    assert "| Total | 4 |" in counts_section
    assert "Core intent page type: blog/guide" in counts_section
    assert "Decision: continue" in counts_section
    assert "DECISION: continue" in completed.stdout


def test_category_majority_stops(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [
            ("https://shop.com/c/1", "Cat 1", "category"),
            ("https://shop.com/c/2", "Cat 2", "category"),
            ("https://shop.com/p/1", "Item", "product"),
            ("https://a.com/post", "Post A", "blog/guide"),
        ],
    )

    completed = _run(serp_intent_path)

    assert completed.returncode == 0, completed.stderr
    counts_section = _counts_section(serp_intent_path)
    assert "Core intent page type: category" in counts_section
    assert "Decision: stop" in counts_section
    assert "DECISION: stop" in completed.stdout


def test_blog_tied_for_first_stops(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [
            ("https://a.com/post", "Post A", "blog/guide"),
            ("https://b.com/post", "Post B", "blog/guide"),
            ("https://shop.com/c/1", "Cat 1", "category"),
            ("https://shop.com/c/2", "Cat 2", "category"),
        ],
    )

    completed = _run(serp_intent_path)

    assert completed.returncode == 0, completed.stderr
    counts_section = _counts_section(serp_intent_path)
    assert "Core intent page type: tie between blog/guide and category" in counts_section
    assert "Decision: stop" in counts_section


def test_escaped_pipe_in_title_keeps_columns(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [
            ("https://a.com/post", r"Costume Ideas \| 133 Best", "blog/guide"),
        ],
    )

    completed = _run(serp_intent_path)

    assert completed.returncode == 0, completed.stderr
    assert "| blog/guide | 1 |" in _counts_section(serp_intent_path)


def test_rerun_replaces_counts_instead_of_duplicating(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [("https://a.com/post", "Post A", "blog/guide")],
    )

    _run(serp_intent_path)
    completed = _run(serp_intent_path)

    assert completed.returncode == 0, completed.stderr
    serp_intent_text = serp_intent_path.read_text(encoding="utf-8")
    assert serp_intent_text.count("## Page type counts") == 1
    assert serp_intent_text.count("Decision: continue") == 1
    assert "## AI Overview" in serp_intent_text


def test_blank_line_kept_before_next_heading(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [("https://a.com/post", "Post A", "blog/guide")],
    )

    _run(serp_intent_path)

    serp_intent_text = serp_intent_path.read_text(encoding="utf-8")
    assert "Decision: continue\n\n## AI Overview" in serp_intent_text


def test_unknown_page_type_is_rejected(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [("https://a.com/post", "Post A", "article")],
    )

    completed = _run(serp_intent_path)

    assert completed.returncode == 1
    assert "article" in completed.stderr


def test_other_without_detail_is_rejected(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [("https://www.pinterest.com/ideas/x", "Ideas", "other")],
    )

    completed = _run(serp_intent_path)

    assert completed.returncode == 1
    assert "other" in completed.stderr


def test_missing_counts_heading_is_rejected(tmp_path: Path) -> None:
    serp_intent_path = _serp_intent_file(
        tmp_path,
        [("https://a.com/post", "Post A", "blog/guide")],
    )
    serp_intent_path.write_text(
        serp_intent_path.read_text(encoding="utf-8").replace(
            "## Page type counts\n", ""
        ),
        encoding="utf-8",
    )

    completed = _run(serp_intent_path)

    assert completed.returncode == 1
    assert "Page type counts" in completed.stderr
