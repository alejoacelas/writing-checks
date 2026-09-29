#!/usr/bin/env python3
# /// script
# dependencies = ["markdown-it-py==4.0.0", "pyyaml>=6,<7"]
# ///
"""Deterministic writing checks. See README.md for the exact rubric."""
import argparse
from dataclasses import dataclass
import json
from pathlib import Path
import re
from statistics import median
import sys

from markdown_it import MarkdownIt
import yaml

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PATHS = [ROOT / "examples"]
MARKDOWN = MarkdownIt("commonmark").enable("table")
RULES = {
    1: "Body sentences: at most 40 words",
    2: "At most one undefined acronym among API, CLI, XML and CDP",
    4: "Recommendation before the first options inventory",
    5: "No production commentary or inline evidence labels",
    6: "No third-person self-reference",
    7: "Paragraphs: maximum 80 words; median at most 45",
    8: "List items: at most 50 words",
    9: "Title: at most 14 words",
    11: "Semicolons: at most one per 200 body words",
    12: "No paired em dashes within a sentence",
    13: "Parenthetical asides: at most ten words",
    16: "Answer before sourcing note",
    17: "No coaching-call framing",
    18: "No .md filenames in reader-facing link labels",
    19: "Separate parallel inline labels into distinct items",
    20: "Em dashes: at most one per 100 body words",
    21: "No substantial stacked asides within a sentence",
    22: "At most one contrast-framed sentence",
    23: "At most two hyphenated compounds within a sentence",
}
GLOSSARY = {
    "API": "application programming interface",
    "CLI": "command line interface",
    "XML": "extensible markup language",
    "CDP": "chrome devtools protocol",
}
PRODUCTION = re.compile(r"\b(?:no entry behind it|talking points|entry carries|entries carry|"
                        r"each statement links to the entry|raw material for improving)\b", re.I)
EVIDENCE_LABEL = re.compile(r"\((?:inferred|reported|tried|documented)\b", re.I)
# Deliberately narrow: two short sentence-initial labels, not arbitrary colons.
INLINE_LABEL = re.compile(r"^[A-Z][\w’'-]*(?:\s+[\w’'-]+)?:\s+\S")
SELF = re.compile(r"\bAlejo(?:[’']s|\s+(?:recommends|opens|says|suggests|teaches|"
                  r"advises|walks|uses|sets|explains))\b", re.I)
COACHING = re.compile(r"\b(?:on (?:coaching )?calls|my workshop line|the habit I teach|"
                      r"the rule I give|what I (?:tell|teach) people|what I set up on calls)\b", re.I)
SOURCES = re.compile(r"^(?:\d+[.)]\s*)?(?:sources?|references|bibliography)$", re.I)
FURTHER = re.compile(r"^(?:go deeper|further reading|see also|read next|related (?:guides|reading))$", re.I)
NOTE = re.compile(r"\b(?:confidence:|overview\s*[—:]|historical reference:|"
                  r"not (?:been )?reverified|sources? (?:checked|consulted):)", re.I)
OPTIONS = re.compile(r"\b(?:vs\.?|versus|comparison|which to (?:choose|reach for)|"
                     r"choose a pattern|where controls can appear)\b", re.I)
RECOMMEND = re.compile(
    r"\b(?:recommend(?:ation|ed)?|default to|(?:right|your) default|default choice|start (?:with|in)|"
    r"(?:choose|pick|prefer|try|reach for)\b|"
    r"(?:^|[.!?]\s+)(?:use|keep|install)\b)", re.I)


def words(text):
    # Hyphenated words and contractions count once; standalone punctuation doesn't.
    return re.findall(r"\b\w+(?:[’'’-]\w+)*\b", re.sub(r"https?://\S+", "", text), re.UNICODE)


def sentences(text):
    # Keep version numbers, filenames, initials and common abbreviations intact.
    protected = re.sub(r"\b(?:e\.g\.|i\.e\.|vs\.|Mr\.|Dr\.|[A-Z]\.)",
                       lambda m: m[0].replace(".", "\ue000"), text)
    return [s.replace("\ue000", ".") for s in re.split(r"(?<=[.!?])\s+", protected)]


def visible(children, code=True):
    return "".join(t.content if t.type in {"text", "code_inline"} else
                   " " if t.type in {"softbreak", "hardbreak"} else
                   visible(t.children or [], code) if t.type == "image" else ""
                   for t in children if code or t.type != "code_inline")


def unquote(text):
    return re.sub(r'“[^”]*”|"[^"\n]*"|‘[^’]*’|(?<!\w)\x27[^\x27\n]*\x27(?!\w)', "", text)


def parentheses(text):
    stack = []
    for i, character in enumerate(text):
        if character == "(":
            stack.append(i)
        elif character == ")" and stack:
            start = stack.pop()
            if not stack:
                yield text[start:i + 1]


def body_paragraphs(blocks):
    """Reader-facing paragraphs, excluding bibliographies and status headers."""
    return [b for b in blocks if b.kind == "paragraph" and not b.quoted
            and not SOURCES.match(b.section) and not FURTHER.match(b.section)
            and not NOTE.search(b.text)
            and not re.match(r"^(?:Last updated|Updated|\d{4}-\d\d-\d\d)\b", b.text)]


def asides(block):
    """Parentheses other than link-only or author/year citations."""
    for parenthesis in parentheses(block.prose):
        aside = parenthesis[1:-1]
        remainder = aside
        for label, _ in block.links:
            remainder = remainder.replace(label, "")
        citation = not remainder.strip(" ;,·") or bool(re.fullmatch(
            r"[A-Z][\w .,&’'-]*,?\s+\d{4}[a-z]?(?:;\s*[A-Z][\w .,&’'-]*,?\s+\d{4}[a-z]?)*", aside))
        if not citation:
            yield parenthesis


def clean_prose(reading):
    """Prose for checks 20–23, omitting quotations, citations and evidence labels."""
    clean = []
    for b in reading:
        text = b.prose
        keep = set(asides(b))
        for parenthesis in parentheses(b.prose):
            if parenthesis not in keep or EVIDENCE_LABEL.match(parenthesis):
                text = text.replace(parenthesis, "")
        clean.append((b.line, unquote(text)))
    return clean


def style_findings(reading):
    """The four calibrated style signals, shared with the calibration report."""
    clean = clean_prose(reading)
    rows = [(line, s) for line, text in clean for s in sentences(text)]
    findings = []

    def add(rule, line, reason, excerpt):
        findings.append({"rule": rule, "line": line, "reason": reason, "excerpt": excerpt})

    body_words = sum(len(words(b.text)) for b in reading)
    dashes = sum(text.count("—") for _, text in clean)
    if dashes * 100 > body_words:
        for line, text in clean:
            if "—" in text:
                add(20, line, f"{dashes} em dashes in {body_words} body words; maximum one per 100", text)
    contrasts = []
    for line, sentence in rows:
        brackets = list(parentheses(sentence))
        long_brackets = [a for a in brackets if len(words(a)) >= 4]
        outside = sentence
        for a in brackets:
            outside = outside.replace(a, "")
        if len(long_brackets) >= 2 or (long_brackets and "—" in outside):
            add(21, line, "Two substantial parentheticals, or one plus an external em dash", sentence)
        if re.search(r",\s+not\b|—\s+not\b|\bnot\b.{1,100}\bbut\b", sentence, re.I):
            contrasts.append((line, sentence))
        compounds = re.findall(r"\b[a-zA-Z]+(?:-[a-zA-Z]+)+\b", sentence)
        if len(compounds) >= 3:
            add(23, line, f"{len(compounds)} hyphenated compounds in one sentence; maximum two", sentence)
    if len(contrasts) >= 2:
        for line, sentence in contrasts:
            add(22, line, f"{len(contrasts)} contrast-framed sentences; maximum one", sentence)
    return findings


@dataclass
class Block:
    kind: str
    line: int
    end: int
    text: str
    prose: str
    links: list
    section: str
    quoted: bool
    item: int | None


def parse(source):
    meta, offset = {}, 0
    source = source.replace("\r\n", "\n")
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", source, re.S)
    if match:
        meta = yaml.safe_load(match[1]) or {}
        if not isinstance(meta, dict):
            raise ValueError("frontmatter must be a mapping")
        offset = source[:match.end()].count("\n")
        source = source[match.end():]
    # Comments and review annotations are private, not reader-facing. Keep line numbers.
    source = re.sub(r"<!--.*?-->|\{>>.*?<<\}",
                    lambda m: "\n" * m[0].count("\n"), source, flags=re.S)
    tokens = MARKDOWN.parse(source)
    blocks, tables, lists, items = [], [], [], []
    section_stack = []
    quote_depth, body_rows, table_line = 0, 0, None
    in_body = False
    for i, token in enumerate(tokens):
        kind = token.type
        if kind == "blockquote_open":
            quote_depth += 1
        elif kind == "blockquote_close":
            quote_depth -= 1
        elif kind in {"bullet_list_open", "ordered_list_open"}:
            lists.append({"line": offset + token.map[0] + 1, "count": 0,
                          "level": token.level, "quoted": bool(quote_depth)})
        elif kind == "list_item_open":
            items.append(offset + token.map[0] + 1)
            for lst in reversed(lists):
                if token.level == lst["level"] + 1:
                    lst["count"] += 1
                    break
        elif kind == "list_item_close":
            items.pop()
        elif kind == "table_open":
            table_line, body_rows = offset + token.map[0] + 1, 0
        elif kind == "tbody_open":
            in_body = True
        elif kind == "tbody_close":
            in_body = False
        elif kind == "tr_open" and in_body:
            body_rows += 1
        elif kind == "table_close":
            tables.append((table_line, body_rows, bool(quote_depth)))
            table_line = None
        elif kind == "inline":
            previous = tokens[i - 1]
            block_kind = previous.tag if previous.type == "heading_open" else (
                "cell" if table_line is not None else "paragraph")
            children = token.children or []
            text = visible(children)
            if previous.type == "heading_open":
                level = int(previous.tag[1:])
                while section_stack and section_stack[-1][0] >= level:
                    section_stack.pop()
                section_stack.append((level, text))
            section = next((s for _, s in reversed(section_stack)
                            if SOURCES.match(s) or FURTHER.match(s)), "")
            links = []
            for j, child in enumerate(children):
                if child.type == "link_open":
                    end = next(k for k in range(j + 1, len(children))
                               if children[k].type == "link_close")
                    links.append((visible(children[j + 1:end]), visible(children[:j])))
            blocks.append(Block(block_kind, offset + token.map[0] + 1,
                                offset + token.map[1], text, visible(children, False),
                                links, section, bool(quote_depth), items[-1] if items else None))
    return meta, blocks, tables, lists


def evaluate(source, *, audience="beginner", options=False):
    meta, blocks, tables, lists = parse(source)
    findings = []

    def fail(rule, block, reason, excerpt=None):
        line = block.line if isinstance(block, Block) else block
        text = excerpt if excerpt is not None else block.text
        findings.append({"rule": rule, "line": line, "reason": reason,
                         "excerpt": text})

    title = meta.get("title")
    first_h1 = next((b for b in blocks if b.kind == "h1"), None)
    if title is not None and not isinstance(title, str):
        raise ValueError("frontmatter title must be text")
    title_match = re.search(r"(?m)^title:", source) if title else None
    title_line = source[:title_match.start()].count("\n") + 1 if title_match else first_h1.line if first_h1 else 1
    title = title or (first_h1.text if first_h1 else "")
    if len(words(title)) > 14:
        fail(9, title_line, f"{len(words(title))} words; maximum 14", title)
    body = [b for b in blocks if not b.quoted and not SOURCES.match(b.section)
            and not FURTHER.match(b.section)]
    paragraphs = [b for b in body if b.kind == "paragraph"]
    answer = next((b for b in paragraphs if not NOTE.search(b.text)
                   and not re.match(r"^(?:Last updated|Updated|\d{4}-\d\d-\d\d)\b", b.text)), None)
    reading = body_paragraphs(blocks)
    findings.extend(style_findings(reading))
    for b in reading:
        for sentence in sentences(b.text):
            if len(words(sentence)) > 40:
                fail(1, b, f"{len(words(sentence))}-word sentence; maximum 40", sentence)
        if EVIDENCE_LABEL.search(b.prose):
            fail(5, b, "Rewrite the inline evidence label as a readable qualification")
        if b.item is None and sum(bool(INLINE_LABEL.match(s)) for s in sentences(b.prose)) >= 2:
            fail(19, b, "Two or more short sentence-initial labels; separate these into items")
    plain = [b for b in reading if b.item is None]
    if len(plain) >= 3:
        typical = median(len(words(b.text)) for b in plain)
        if typical > 45:
            representative = min(plain, key=lambda b: abs(len(words(b.text)) - typical))
            fail(7, representative,
                 f"Document median is {typical:g} words across {len(plain)} prose paragraphs; maximum 45")
    semicolon_blocks = [(b, unquote(b.prose).count(";")) for b in reading]
    semicolon_count = sum(n for _, n in semicolon_blocks)
    body_words = sum(len(words(b.text)) for b in reading)
    if semicolon_count >= 2 and semicolon_count * 200 > body_words:
        for b, count in semicolon_blocks:
            if count:
                fail(11, b, f"{semicolon_count} semicolons in {body_words} body words; maximum one per 200")
    for b in blocks:
        if NOTE.search(b.text) and (answer is None or b.line < answer.line):
            if b.kind == "paragraph":
                fail(16, b, "Sourcing note precedes the first substantive paragraph")
    if audience == "beginner":
        # Explicit definitions are verifiable: expansion before acronym, or ACRONYM (expansion).
        seen = title + "\n" + "\n".join(b.text for b in body)
        normalized = seen.lower().replace("-", " ")
        undefined = []
        for acronym, expansion in GLOSSARY.items():
            match = re.search(rf"\b{acronym}s?\b", seen)
            if match and expansion not in normalized[:match.start()] and not re.match(
                    rf"\s*\({re.escape(expansion)}s?\)", normalized[match.end():]):
                b = next((b for b in body if re.search(rf"\b{acronym}s?\b", b.text)), None)
                undefined.append((acronym, b))
        if len(undefined) >= 2:
            for acronym, b in undefined:
                fail(2, title_line if re.search(rf"\b{acronym}s?\b", title) else b.line,
                     f"{len(undefined)} undefined acronyms; {acronym} appears before its expansion",
                     title if re.search(rf"\b{acronym}s?\b", title) else b.text)
    options = options or bool(OPTIONS.search(title + "\n" + "\n".join(
        b.text for b in body if b.kind.startswith("h"))))
    if options:
        inventories = [line for line, _, quoted in tables if not quoted]
        inventories += [lst["line"] for lst in lists if lst["count"] >= 3 and not lst["quoted"]
                        and any(b.item == lst["line"] and b in body for b in blocks)]
        if inventories:
            first = min(inventories)
            if not any(RECOMMEND.search(b.text) for b in paragraphs if b.line < first):
                fail(4, first, "No recommendation marker before first table or 3-item list",
                     next((b.text for b in blocks if b.line >= first), "Inventory"))
    item_blocks = {}
    for b in blocks:
        if b.quoted or SOURCES.match(b.section):
            continue
        if b.item is not None and not (SOURCES.match(b.section) or FURTHER.match(b.section)):
            item_blocks.setdefault(b.item, []).append(b)
        for label, prefix in b.links:
            if re.search(r"\b[\w.-]+\.md\b", label, re.I):
                # Filename instructions must put the explicit operation immediately before the link.
                if not re.search(r"\b(?:open|edit|read|create|save|update)\s+(?:the\s+)?$", prefix, re.I):
                    fail(18, b, "Filename in link label", label)
        if SOURCES.match(b.section) or FURTHER.match(b.section):
            continue
        for rule, pattern in [(5, PRODUCTION), (6, SELF), (17, COACHING)]:
            match = pattern.search(b.prose)
            if match:
                fail(rule, b, f"Contains {match[0]!r}")
        if b in reading and b.item is None:
            if len(words(b.text)) > 80:
                fail(7, b, f"{len(words(b.text))} words; maximum 80")
        if b.kind not in {"paragraph", "cell"}:
            continue
        prose = unquote(b.prose)
        if any(s.count("—") >= 2 for s in sentences(prose)):
            fail(12, b, "Two or more em dashes within one sentence")
        for parenthesis in asides(b):
            if len(words(parenthesis)) > 10:
                fail(13, b, f"{len(words(parenthesis))}-word parenthesis; maximum ten", parenthesis)
    for line, group in item_blocks.items():
        text = " ".join(b.text for b in group)
        if len(words(text)) > 50:
            fail(8, line, f"{len(words(text))} words; maximum 50", text)
    return sorted(findings, key=lambda f: (f["rule"], f["line"]))


def files(paths):
    found = set()
    for path in paths:
        path = Path(path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
        if path.is_file():
            found.add(path.resolve())
        else:
            for file in path.rglob("*.md"):
                if any(p.startswith(".") or p in {"node_modules", "__pycache__"}
                       for p in file.relative_to(path).parts):
                    continue
                if file.name in {"AGENTS.md", "DECISIONS.md", "PLAN.md", "feedback-log.md"}:
                    continue
                found.add(file.resolve())
    return sorted(found)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Markdown files or directories (default: bundled examples)")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--checks", default=",".join(map(str, RULES)), help="Comma-separated IDs, e.g. 1,7,8")
    parser.add_argument("--audience", choices=["beginner", "technical"], default="beginner")
    parser.add_argument("--options-guide", action="store_true", help="Apply check 4 regardless of title/headings")
    args = parser.parse_args(argv)
    try:
        selected = set(map(int, args.checks.split(",")))
        if not selected or not selected <= RULES.keys():
            raise ValueError("Check IDs must be among: " + ", ".join(map(str, RULES)))
        paths = args.paths or [p for p in DEFAULT_PATHS if p.exists()]
        documents = files(paths)
        if not documents:
            raise ValueError("No Markdown documents found")
        results = []
        for path in documents:
            findings = [f for f in evaluate(path.read_text(), audience=args.audience,
                                           options=args.options_guide) if f["rule"] in selected]
            results.append({"path": str(path), "checks": [
                {"id": rule, "name": RULES[rule],
                 "status": "SKIP" if rule == 2 and args.audience == "technical" else
                           "FAIL" if any(f["rule"] == rule for f in findings) else "PASS",
                 "findings": [f for f in findings if f["rule"] == rule]}
                for rule in sorted(selected)]})
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    failed = sum(c["status"] == "FAIL" for r in results for c in r["checks"])
    if args.format == "json":
        print(json.dumps({"documents": results, "failed_checks": failed}, indent=2, ensure_ascii=False))
    else:
        for result in results:
            print(result["path"])
            print("  " + " ".join(f"{c['id']}:{c['status']}" for c in result["checks"]))
            for check in result["checks"]:
                for f in check["findings"]:
                    excerpt = " ".join(f["excerpt"].split())
                    print(f"  L{f['line']} [{f['rule']}] {f['reason']}: {excerpt[:220]}")
        print(f"{len(results)} documents; {failed} failed document/check pairs.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
