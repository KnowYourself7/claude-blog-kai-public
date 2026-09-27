#!/usr/bin/env python3
"""Count page types in serp-intent.md and fill its `## Page type counts` section.

Reads the organic results table (columns: Rank | URL | Title | Page type),
counts rows per page type, picks the most common type as the core intent
page type, and decides whether the brief continues (K-015):

- continue: blog/guide has strictly the most rows
- stop: any other type has the most rows, or blog/guide ties for first

Usage:
    python3 count_serp_types.py briefs/<slug>/serp-intent.md

Exit 0 after writing the section (the last stdout line is
`DECISION: continue` or `DECISION: stop`). Exit 1 on a malformed file.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PAGE_TYPES = ("blog/guide", "category", "product", "other")
COUNTS_HEADING = "## Page type counts"
TABLE_HEADER_CELLS = ["Rank", "URL", "Title", "Page type"]


def _split_table_row(table_line: str) -> list[str]:
    """Split a markdown table row on unescaped pipes."""
    inner_text = table_line.strip().strip("|")
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", inner_text)]


def _read_page_types(serp_intent_lines: list[str]) -> list[str]:
    page_types_found: list[str] = []
    inside_results_table = False
    for table_line in serp_intent_lines:
        if not table_line.strip().startswith("|"):
            if inside_results_table:
                break
            continue
        row_cells = _split_table_row(table_line)
        if row_cells == TABLE_HEADER_CELLS:
            inside_results_table = True
            continue
        if not inside_results_table or set("".join(row_cells)) <= set("-: "):
            continue
        if len(row_cells) != len(TABLE_HEADER_CELLS):
            raise ValueError(f"row does not have 4 columns: {table_line.strip()}")
        page_types_found.append(row_cells[3])
    if not page_types_found:
        raise ValueError("no rows found in the Rank | URL | Title | Page type table")
    return page_types_found


def _normalize_page_type(page_type_cell: str) -> str:
    if page_type_cell in ("blog/guide", "category", "product"):
        return page_type_cell
    if page_type_cell.startswith("other:") and page_type_cell[len("other:"):].strip():
        return "other"
    if page_type_cell == "other":
        raise ValueError("page type 'other' must say what it is, e.g. 'other: video'")
    raise ValueError(
        f"unknown page type '{page_type_cell}'; use blog/guide, category, product, or other: <what>"
    )


def build_counts_section(page_types_found: list[str]) -> tuple[str, str]:
    """Return the section text and the decision (continue or stop)."""
    type_counts = {page_type: 0 for page_type in PAGE_TYPES}
    for page_type_cell in page_types_found:
        type_counts[_normalize_page_type(page_type_cell)] += 1

    highest_count = max(type_counts.values())
    top_types = [page_type for page_type in PAGE_TYPES if type_counts[page_type] == highest_count]
    if len(top_types) == 1:
        core_type_text = top_types[0]
    else:
        core_type_text = "tie between " + " and ".join(top_types)
    decision = "continue" if top_types == ["blog/guide"] else "stop"

    section_lines = [COUNTS_HEADING, "", "| Page type | Count |", "|---|---|"]
    section_lines += [f"| {page_type} | {type_counts[page_type]} |" for page_type in PAGE_TYPES]
    section_lines += [
        f"| Total | {len(page_types_found)} |",
        "",
        f"Core intent page type: {core_type_text}",
        f"Decision: {decision}",
        "",
    ]
    return "\n".join(section_lines), decision


def fill_counts_section(serp_intent_text: str) -> tuple[str, str, str]:
    serp_intent_lines = serp_intent_text.splitlines()
    heading_indexes = [
        line_index for line_index, text_line in enumerate(serp_intent_lines)
        if text_line.strip() == COUNTS_HEADING
    ]
    if len(heading_indexes) != 1:
        raise ValueError(f"expected exactly one '{COUNTS_HEADING}' heading")
    heading_index = heading_indexes[0]
    next_heading_index = next(
        (
            line_index for line_index in range(heading_index + 1, len(serp_intent_lines))
            if serp_intent_lines[line_index].startswith("## ")
        ),
        len(serp_intent_lines),
    )

    counts_section, decision = build_counts_section(_read_page_types(serp_intent_lines))
    updated_lines = (
        serp_intent_lines[:heading_index]
        + counts_section.split("\n")
        + serp_intent_lines[next_heading_index:]
    )
    return "\n".join(updated_lines) + "\n", counts_section, decision


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: count_serp_types.py <path/to/serp-intent.md>", file=sys.stderr)
        return 1
    serp_intent_path = Path(argv[1])
    try:
        updated_text, counts_section, decision = fill_counts_section(
            serp_intent_path.read_text(encoding="utf-8")
        )
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    serp_intent_path.write_text(updated_text, encoding="utf-8")
    print(counts_section)
    print(f"DECISION: {decision}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
