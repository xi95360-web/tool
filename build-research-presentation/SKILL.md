---
name: build-research-presentation
description: Build rigorous, evidence-dense academic presentations for research proposals and journal clubs. Use when the user asks to plan, create, revise, audit, or rehearse a proposal defense, qualifying proposal, literature seminar, paper discussion, or journal-club PPT/PPTX/PDF; turn papers, a Zotero collection, data, or a research idea into slides; or select suitable references for those formats. Enforces a user questionnaire, claim-level evidence traceability, figure-level analysis, communication-first action titles and ghost-deck structure, explicit citations, scientific logic checks, speaker notes, timing, and rendered-slide quality review.
---

# Build Research Presentation

Create presentations whose logic can survive expert questioning. Treat visual polish as support for scientific reasoning, never as a substitute for evidence.

## Non-negotiable Rules

1. Never present a paper, DOI, result, sample size, statistic, control, mechanism, preliminary datum, or quotation as existing unless it is verified. Proposed controls, mechanisms, and designs are allowed only when labeled **PROPOSED**; every quantitative assumption must come from a verified source or user input, otherwise remain unknown or be explored with a sensitivity range.
2. Use one controlled evidence-status vocabulary in the claim ledger and on the relevant slide:
   - `PUBLISHED`: verified published or archived evidence;
   - `USER_DATA`: user-provided unpublished result;
   - `PROPOSED`: future design, hypothesis, prediction, or proposed model;
   - `INFERENCE`: interpretation not directly demonstrated by a source;
   - `EVIDENCE_GAP`: unresolved or inaccessible support.
   Conceptual models inherit one of these statuses; “conceptual” is a content type, not an evidence status. Do not mechanically label ordinary task metadata or instructions. Never rely on color alone to distinguish statuses.
3. Do not produce a finished evidence-bearing deck until its essential sources have been read. If sources are missing, return the questionnaire and a reference-selection shortlist or gap table first.
4. Make every non-administrative slide scientifically useful. A content slide must have a claim or question, an evidence object, a bounded interpretation, a source locator, and a spoken transition.
5. Use real data figures, redrawn mechanisms, experimental schematics, models, or comparison tables before decorative imagery. Never generate fake scientific data. Clearly label conceptual illustrations.
6. Preserve uncertainty and negative evidence. State what a result does **not** establish.
7. Make one defensible argument per presentation. Use action titles that state the slide's evidence-bounded takeaway; use a precise question only when the answer is intentionally unresolved. Replace “Results” with “Knockdown reduces invasion without changing viability.”
8. Keep slides editable when the user requests PPTX. Also export PDF when possible.

## Read the Relevant Resources

Always read:

- `references/user-questionnaire-zh.md` or `references/user-questionnaire-en.md`, matching the user
- `references/slide-evidence-matrix.md`
- `references/literature-search-record.md`
- `references/content-design-standard.md`
- `references/communication-first-design.md`
- `references/quality-gates.md`

Then read one route:

- Proposal: `references/proposal-route.md`
- Journal club: `references/journal-club-route.md`

Read `references/source-principles.md` when explaining, auditing, or applying the original course principles.

Retain `references/third-party-notices.md` when redistributing or maintaining the skill.

## Workflow

### 1. Establish the Assignment

Identify:

- route: `proposal` or `journal-club`;
- purpose, audience, discipline, language, duration, Q&A time, venue, and required format;
- the one sentence the audience should remember;
- user constraints: template, slide limit, required questions, citation style, and deadline.

Use the matching questionnaire. Do not force the user to repeat information already present in the conversation or attached files. If enough information exists, fill the questionnaire on the user's behalf and flag assumptions. Never infer permission to disclose unpublished data, confidentiality status, figure rights, or human/animal/dual-use approvals.

Use the minimum viable intake before asking the full questionnaire:

- all routes: audience, total speaking/Q&A time, language, output format, and source entry point;
- journal club: a focal paper **or** permission and scope to search for one;
- proposal: the problem, available preliminary evidence, available resources, and whether exploratory/discovery aims are acceptable.

Default low-risk presentation settings when necessary and label them as assumptions. Ask only questions whose answers change source selection, scientific scope, or the artifact.

### 2. Secure the Evidence Base

Accept PDFs, DOI/PMID lists, URLs, BibTeX/RIS, Zotero exports or collections, data files, protocols, and notes.

For each source and claim, record:

- verified citation and persistent identifier;
- role: focal paper, background, gap, method, benchmark, counterevidence, or feasibility;
- exact supporting location: page, section, figure, panel, table, or dataset column;
- source statement or data used;
- claim supported and support type: direct, partial, contextual, or conflicting;
- caveat, study type, evidence status, access level, and verification state.

Use these operational definitions:

- **Essential source:** removing it would break the central gap, hypothesis, main result, feasibility claim, or final verdict.
- **Read:** for a focal/core paper, inspect the full main text, all captions, relevant methods, and relevant supplement; for a supporting primary paper, inspect the full sections and figures that bear on the claim; for a review, inspect the relevant section and trace decisive claims to primary work; for a method source, inspect validation and limitations.
- **Verified metadata:** cross-check the persistent identifier and bibliographic fields against a publisher, DOI registry, PubMed, or the authoritative repository.
- **Supports:** mark whether the source directly demonstrates, partially supports, only contextualizes, or conflicts with the claim.
- **Critical issue:** fabricated/unresolved support, a missing premise that changes the conclusion, a misleading figure transformation, an unreadable evidence object, a broken artifact, or a route-specific gate failure.

If essential full text, a decisive caption/supplement, or authoritative metadata is inaccessible, record the access failure and keep the affected claim as `EVIDENCE_GAP`. Do not use an abstract alone to support a decisive claim.

If reference selection is needed:

1. Ask the user whether to use supplied sources, search a specified library, or search the literature.
2. Record databases/libraries, dates, query strings, filters, inclusion/exclusion rules, forward/backward citation checks, and search limitations in `references/literature-search-record.md`.
3. Return 3–5 **presentation candidates** in the selection table from the questionnaire. This shortlist is not the complete evidence base.
4. Rank by topical fit, methodological clarity, evidential depth, discussion value, recency where relevant, and accessibility.
5. Explain tradeoffs without using journal impact factor as a proxy for paper quality.
6. Wait for selection only when the choice materially changes the presentation. Otherwise proceed with the strongest documented option and state the assumption.

Operationalize vague preferences before ranking. For example, translate “recent” into a date range and “strong figures” into testable features such as causal perturbation, rescue, orthogonal validation, explicit controls, readable quantitative panels, and sufficient methods/statistics.

Use primary papers for specific claims. Use reviews to orient the field and trace claims back to primary evidence. Label preprints and non-peer-reviewed sources. Verify all current metadata before citing it.

Do not claim a field-wide gap from the 3–5-paper shortlist. For a proposal gap or journal-club field comparison, search multiple concept variants and, where accessible, more than one independent database/library; follow citations backward and forward; explicitly seek null, conflicting, and boundary-setting evidence; and stop only when new searches cease changing the claim map. If coverage is limited, describe the result as a scoped search rather than exhaustive or systematic.

### 3. Write the Scientific Spine Before Slides

Produce:

- a one-sentence thesis or central question;
- 2–4 audience takeaways;
- a logic chain in the form `known → unresolved gap → question/hypothesis → test → result/prediction → implication`;
- a section outline with time allocation;
- an evidence map and claim ledger using `references/slide-evidence-matrix.md`.

Write the action-title sequence before layout. Run the ghost-deck test: titles alone must express one coherent, evidence-bounded argument, and each title must make the next slide necessary. A title sequence that reads as a topic list fails.

Reject an outline if:

- a conclusion appears before its premises;
- a causal claim rests only on correlation;
- an aim does not test the stated hypothesis;
- a result lacks an appropriate control or comparison;
- a slide merely repeats the paper or proposal text;
- adjacent sections have no explicit transition;
- the deck tries to present the whole paper or proposal instead of one defensible main argument;
- the ghost deck introduces a claim before its support or overstates the claim ledger.

### 4. Apply the Route

Follow `references/proposal-route.md` or `references/journal-club-route.md`.

Keep the introduction to the minimum background needed to understand the question. Allocate the largest share of time to evidence, experimental logic, and interpretation. For short talks, reduce the number of claims instead of shrinking text or rushing.

### 5. Specify Every Slide

Before building, write a slide specification with:

- evidence-bounded action title or precise unresolved question;
- scientific purpose;
- dominant visual/evidence exhibit;
- 1–3 annotations that direct attention;
- explicit “so what” annotation on the decisive observation;
- exact source locator;
- interpretation and limitation;
- one-sentence takeaway;
- transition to the next slide;
- estimated speaking time;
- optional backup-slide link.

Put the central question or hypothesis on the title slide. Do not create a standalone decorative acknowledgments or “Thank you” slide unless an institutional template requires it; combine acknowledgments with a conclusion/Q&A slide or place them in backup. Section dividers must include the next scientific question or a compact roadmap.

### 6. Build the Deck

Use the available presentation-generation skill (for example, Presentations or PPTX) and follow its technical instructions. When source PDFs are involved, use the PDF skill to extract text and inspect rendered pages. If no supported deck-generation or rendering path is available, stop at a validated slide specification and label the deliverable incomplete rather than pretending a PPTX/PDF was produced.

Visual rules:

- one main idea per slide;
- prioritize one dominant scientific exhibit; use several panels only when they form one comparison or inference;
- redraw or simplify paper figures for projection while preserving values and meaning;
- enlarge labels, lines, structures, axes, and legends;
- explain axes, units, groups, sample size, error bars, statistical tests, controls, and panel order;
- directly label key curves or structures where possible;
- use restrained, color-blind-safe emphasis;
- use consistent typography, spacing, arrow weights, and object scales;
- use animation only to reveal a reasoning sequence, not for decoration.

Do not paste unreadable multi-panel figures. Split them into multiple slides or crop to the discussed panel while retaining attribution and enough context to avoid misleading the audience.

Apply the communication-first defaults in `references/communication-first-design.md`. Institutional templates and accessibility needs may override its visual defaults, but not its argument, attribution, or evidence rules.

### 7. Cite on the Slide

Place a compact citation beside or below the supported content, not only in a final bibliography. Prefer:

- `Author et al., Journal Year, DOI` for papers;
- database name, record/access date, and original source where available for data;
- `Adapted from ...` when redrawing;
- `User-provided data, date/experiment ID` for unpublished results;
- `Proposed experiment` or `Conceptual model` for future work.

Keep a full reference list in backup slides or an accompanying source file. Verify that every citation resolves and supports the nearby claim.

### 8. Add Notes, Timing, and Backup

Speaker notes should contain reasoning that is too detailed for the slide:

- what to say;
- what not to overclaim;
- transition sentence;
- likely expert objection;
- concise answer and backup-slide pointer.

Target roughly one slide per minute only as a planning heuristic. Give complex evidence slides more time. Rehearse to finish about 5–10% before the hard talk limit and reserve Q&A separately. Never cut the conclusion to recover time.

Prepare backup slides for controls, full methods, sensitivity analyses, alternative models, extra literature, risk mitigation, and likely questions.

### 9. Validate the Rendered Artifact

Run every gate in `references/quality-gates.md`.

For PPTX:

1. render/export the full deck;
2. inspect every slide image, not just the source XML or text;
3. check overflow, overlap, clipping, contrast, tiny labels, distorted figures, and inconsistent alignment;
4. correct and rerender until no critical issue remains.

Record objective QA evidence: artifact open test, slide count, rendered-image count, notes presence, unresolved links/identifiers, font or overflow findings, and the reviewer observation for each manual gate. The render count must equal the deck slide count.

Also compare the final deck against the evidence matrix. A visually attractive slide fails if its claim is unsupported or its figure cannot be read at presentation distance.

Read the rendered action titles in order one final time. Confirm that the ghost deck, the claim ledger, and the spoken transitions express the same argument.

## Required Deliverables

Unless the user asks for a smaller scope, provide:

1. editable `.pptx`;
2. rendered `.pdf`;
3. completed slide-evidence matrix;
4. reference list with identifiers and source roles;
5. speaker notes and timing;
6. backup slides;
7. concise quality-gate report;
8. assumptions and unresolved evidence gaps.

If the task is only planning or auditing, provide the corresponding subset and state what is still required before deck generation.

If PPTX or PDF generation, rendering, or open-testing is unavailable, provide the safe subset, list the missing artifact, and mark the result **not final**.

## Completion Standard

A deck is complete only when:

- the thesis, section order, and transitions form a valid argument;
- the action titles pass the ghost-deck test without exceeding the evidence;
- every content slide passes the slide contract;
- proposal aims are falsifiable and feasible, or journal-club results are analyzed figure by figure;
- sources are verified and traceable;
- uncertainties, limitations, and alternatives are explicit;
- content fits the allotted time;
- the rendered deck is readable, balanced, consistent, and free of layout defects;
- the closing answers the opening question without adding unsupported claims and remains visible during Q&A.
