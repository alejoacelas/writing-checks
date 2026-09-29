# Writing rubric

## Checks

Checks identify passages to review. A failure is not an instruction to remove
useful detail. Each rule contributes at most one failed point, even when it
produces several findings. IDs 3, 10, 14 and 15 are retired; 19–23 are newer additions.

| ID | Pass condition |
| --- | --- |
| 1 | Every body sentence has at most 40 words. |
| 2 | At most one of API, CLI, XML and CDP appears before its expansion; skipped for technical audiences. |
| 4 | Recognized comparison guides have a recommendation marker before their first table or list of at least three items. |
| 5 | No specified production phrase or inline evidence label. |
| 6 | No specified third-person reference to Alejo. |
| 7 | Non-list body paragraphs have at most 80 words; with at least three such paragraphs, their median is at most 45 words. |
| 8 | Each list item has at most 50 words. |
| 9 | The frontmatter title, or first H1 if absent, has at most 14 words. |
| 11 | At most one semicolon per 200 body words; a single semicolon is always allowed. |
| 12 | No sentence contains two or more em dashes outside code or quotation. |
| 13 | Parenthetical asides have at most ten words, excluding citations. |
| 16 | The answer precedes sourcing notes; a date alone is allowed. |
| 17 | No specified coaching-call framing. |
| 18 | No `.md` filenames in navigation link labels; source bibliographies and explicit file operations are exempt. |
| 19 | A prose paragraph has fewer than two short, sentence-initial labels such as “Files:” and “Billing:”. |
| 20 | At most one em dash per 100 body words. |
| 21 | No sentence has two parentheticals of at least four words each, or one plus an em dash outside parentheses. |
| 22 | At most one sentence uses a recognized contrast pattern: “X, not Y”, “X — not Y” or “not X but Y”. |
| 23 | At most two alphabetic hyphenated compounds occur in one sentence. |

Paragraph median is part of rule 7, not an additional point. Evidence labels are
part of rule 5. Semicolon findings show the document count and word denominator.
The median finding highlights a representative paragraph and reports the median
and paragraph count; it does not imply that paragraph alone is the problem.

The broader review question behind rule 19 is: **does this paragraph present
several independently useful choices that deserve separate items?** The automatic
check recognizes only one- or two-word labels followed by a colon and content at
the start of a sentence. It intentionally misses unlabeled or longer choices;
review those manually. It excludes lists, quotes, code and source sections.

## Exact conventions

- **Words and sentences:** Unicode words; hyphenated words and contractions count
  once. URLs and punctuation do not count. Visible inline-code text and link
  labels count toward lengths. Sentences split on `.`, `!` or `?` followed by
  whitespace, protecting common abbreviations and initials. This is a heuristic.
- **Private material and code:** YAML contributes only its public title. HTML
  comments and CriticMarkup review comments are ignored, preserving source lines.
  Fenced and indented code is excluded. Inline code is excluded from prose-pattern
  checks, but included in word counts.
- **Sections:** blockquotes and Sources, References, Bibliography and further-reading
  sections are excluded from body checks. Further-reading headings include Go
  deeper, Further reading, See also, Read next, Related guides and Related reading.
  Source-section filename labels are exempt from 18; further-reading navigation
  labels are still checked. A quoted sourcing warning can still trigger 16.
- **Reading body:** checks 1, the median in 7, 11 and 19 exclude date/status headers
  beginning Last updated, Updated or an ISO date, and paragraphs matching the
  sourcing-note patterns. The 80-word paragraph limit uses the same body. Sentence
  and semicolon checks include list paragraphs; medians exclude lists. Table cells
  do not enter these counts. Quoted inline text counts toward sentence lengths,
  but paired straight/curly quotes are excluded from punctuation checks 11–12.
- **Checks 20–23:** use the same reading body, including list paragraphs, and
  remove inline code, quotations, citation-only parentheses and evidence-label
  parentheticals before matching. Check 20 divides the remaining em-dash count by
  the full visible body word count, including inline code and quotations. It flags
  strictly more than one per 100 words, including one dash in a shorter document.
  Check 21 counts four-word outer parentheticals, with nested text included. Check
  22 counts matching sentences, not individual occurrences; its “not … but” match
  permits up to 100 intervening characters. Check 23 recognizes alphabetic words
  joined by ASCII hyphens; repeated occurrences count separately. These checks
  are individually scored even where they overlap with sentence/aside checks.
- **Lists:** wrapped lines and multiple paragraphs in one item are combined for
  check 8. Nested items are checked separately from their parent.
- **Acronyms:** application programming interface; command-line interface;
  extensible markup language; Chrome DevTools Protocol. An expansion must precede
  first use or follow it immediately in parentheses. Plurals are recognized;
  case and hyphens in expansions are ignored. If two or more are undefined, check
  2 reports all of them. This measures acronym accumulation, not comprehension.
- **Comparisons:** check 4 is enabled by `--options-guide` or title/heading markers
  vs, versus, comparison, which to choose, which to reach for, choose a pattern,
  or where controls can appear. The word options alone no longer activates it.
  Earlier recommendation markers include recommend/recommendation/recommended,
  default to, right default, your default, default choice, start with/in, choose,
  pick, prefer, try, reach for, or sentence-initial use, keep or install. This is
  placement detection; quoted and negated recommendations can still match.
- **Production phrases:** no entry behind it; talking points; entry carries;
  entries carry; each statement links to the entry; raw material for improving.
  Evidence labels are body parentheses beginning inferred, reported, tried or
  documented. Rewrite these as clear qualifications; preserve uncertainty.
- **Self-reference:** Alejo's/Alejo’s, or Alejo followed by recommends, opens,
  says, suggests, teaches, advises, walks, uses, sets or explains.
- **Parentheses:** link-only and author/year citations are exempt; nested asides
  count toward the outer aside. Plain-text titles are not reliably recognized
  as citations.
- **Sourcing notes:** Confidence:, Overview —/Overview:, Historical reference:,
  not reverified, not been reverified, Source(s) checked: or Source(s) consulted:.
- **Coaching phrases:** on calls, on coaching calls, my workshop line, the habit
  I teach, the rule I give, what I tell people, what I teach people, what I set
  up on calls.
- **Filename operations:** a link immediately preceded by open, edit, read,
  create, save or update, optionally followed by the, is exempt from check 18.
