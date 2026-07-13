"""Run reproducible PPTX parser benchmarks against a shared public corpus."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import re
import sys
import time
import tracemalloc
from collections import Counter
from collections.abc import Callable, Sequence
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from pptx2markdown import parse
from pptx2markdown.main_converter.converter_models import render_presentation_markdown

Provider = Callable[[Path], str]


def _pptx2markdown(path: Path) -> str:
    return render_presentation_markdown(parse(path))


def _docling(path: Path) -> str:
    from docling.document_converter import DocumentConverter

    return DocumentConverter().convert(path).document.export_to_markdown()


def _unstructured(path: Path) -> str:
    from unstructured.partition.pptx import partition_pptx

    return "\n".join(str(element) for element in partition_pptx(filename=str(path)))


PROVIDERS: dict[str, Provider] = {
    "pptx2markdown": _pptx2markdown,
    "docling": _docling,
    "unstructured": _unstructured,
}


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+|[^\w\s]", text.casefold(), flags=re.UNICODE)


def _expected_content(golden: dict[str, Any]) -> tuple[str, dict[str, list[str]]]:
    contents: list[str] = []
    by_kind: dict[str, list[str]] = {}
    for slide in golden.get("slides", []):
        for block in slide.get("blocks", []):
            kind = str(block.get("kind", ""))
            if kind in {"image", "attachment", "unsupported"}:
                continue
            content = str(block.get("content", "")).strip()
            if content:
                contents.append(content)
                by_kind.setdefault(kind, []).append(content)
        notes = str(slide.get("notes") or "").strip()
        if notes:
            contents.append(notes)
            by_kind.setdefault("notes", []).append(notes)
    return "\n".join(contents), by_kind


def _recall(expected: Sequence[str], actual: Sequence[str]) -> float:
    if not expected:
        return 1.0
    expected_counts = Counter(expected)
    actual_counts = Counter(actual)
    matched = sum(min(count, actual_counts[token]) for token, count in expected_counts.items())
    return matched / sum(expected_counts.values())


def _score(expected: str, by_kind: dict[str, list[str]], actual: str) -> dict[str, Any]:
    expected_tokens = _tokens(expected)
    actual_tokens = _tokens(actual)
    kind_recall = {
        kind: _recall(_tokens("\n".join(contents)), actual_tokens)
        for kind, contents in sorted(by_kind.items())
    }
    return {
        "text_recall": round(_recall(expected_tokens, actual_tokens), 6),
        "order_similarity": round(
            SequenceMatcher(None, expected_tokens, actual_tokens, autojunk=False).ratio(),
            6,
        ),
        "kind_recall": {key: round(value, 6) for key, value in kind_recall.items()},
        "output_characters": len(actual),
    }


def _version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--goldens", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("benchmark-results.json"))
    parser.add_argument(
        "--providers",
        default="pptx2markdown,docling,unstructured",
        help="Comma-separated provider names",
    )
    args = parser.parse_args()

    requested = [name.strip() for name in args.providers.split(",") if name.strip()]
    unknown = sorted(set(requested) - PROVIDERS.keys())
    if unknown:
        parser.error(f"unknown providers: {', '.join(unknown)}")

    rows: list[dict[str, Any]] = []
    for source in sorted(args.corpus.glob("*.pptx")):
        golden_path = args.goldens / f"{source.stem}.json"
        if not golden_path.is_file():
            continue
        expected, by_kind = _expected_content(json.loads(golden_path.read_text(encoding="utf-8")))
        for name in requested:
            tracemalloc.start()
            started = time.perf_counter()
            try:
                actual = PROVIDERS[name](source)
                status = "ok"
                error = None
            except Exception as exc:  # noqa: BLE001 - benchmark records provider failures.
                actual = ""
                status = "failed"
                error = f"{type(exc).__name__}: {exc}"
            duration = time.perf_counter() - started
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            rows.append(
                {
                    "file": source.name,
                    "provider": name,
                    "status": status,
                    "error": error,
                    "duration_seconds": round(duration, 6),
                    "peak_memory_bytes": peak,
                    **_score(expected, by_kind, actual),
                }
            )

    payload = {
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "packages": {
                name: _version(name)
                for name in (
                    "pptx2markdown",
                    "langchain-pptx2markdown",
                    "docling",
                    "unstructured",
                )
            },
        },
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
