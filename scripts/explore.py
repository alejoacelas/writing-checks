#!/usr/bin/env python3
# /// script
# dependencies = ["markdown-it-py==4.0.0", "pyyaml>=6,<7"]
# ///
"""Build a private, standalone HTML explorer from the current writing corpus."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import webbrowser

from check import ROOT, RULES, SOURCES, FURTHER, DEFAULT_PATHS, evaluate, files, parse, words


def document(path):
    source = path.read_text()
    meta, blocks, _, _ = parse(source)
    findings = evaluate(source)
    failed = sorted({f["rule"] for f in findings})
    provider = meta.get("reference_provider")
    if provider not in {"Stripe", "Django", "GOV.UK", "Chrome"}:
        provider = None
    if provider:
        group = provider
    elif meta.get("kind") == "primer":
        group = "Primers"
    elif meta.get("kind") == "article":
        group = "Articles"
    else:
        group = "Indexes" if path.name in {"README.md", "index.md"} else "Notes"
    source_url = meta.get("source_url")
    title = meta.get("title") or next((b.text for b in blocks if b.kind == "h1"), path.stem)
    count = sum(len(words(b.text)) for b in blocks
                if not b.quoted and not SOURCES.match(b.section) and not FURTHER.match(b.section))
    return {
        "title": title, "path": str(path.relative_to(ROOT.parent)) if path.is_relative_to(ROOT.parent) else str(path),
        "uri": path.as_uri(), "group": group, "reference": bool(provider),
        "source_url": source_url, "words": count,
        "score": len(RULES) - len(failed), "failed": failed, "findings": findings,
        # Reader-facing parsed text only: never embed frontmatter or review comments.
        "blocks": [{"line": b.line, "end": b.end, "text": b.text, "kind": b.kind}
                   for b in blocks],
    }


def build(paths, output):
    documents = [document(path) for path in files(paths)]
    if not documents:
        raise ValueError("No Markdown documents found")
    data = {"rules": RULES, "documents": documents,
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
    # Prevent source text from closing the data script or creating HTML markup.
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c").replace(
        "\u2028", "\\u2028").replace("\u2029", "\\u2029")
    template = Path(__file__).with_name("explorer.html").read_text()
    output.write_text(template.replace("__WRITING_DATA__", payload))
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Files/directories; default: bundled examples")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("explorer.local.html"))
    parser.add_argument("--open", action="store_true", help="Open the generated file in your browser")
    args = parser.parse_args()
    data = build(args.paths or [p for p in DEFAULT_PATHS if p.exists()], args.output)
    print(f"{len(data['documents'])} documents → {args.output.resolve()}")
    if args.open:
        webbrowser.open(args.output.resolve().as_uri())


if __name__ == "__main__":
    main()
