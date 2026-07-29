# Communication-First Academic Design

## Contents

1. Priority order
2. Argument architecture
3. Action titles and ghost deck
4. Exhibit discipline
5. Visual defaults
6. Core slide patterns
7. Timing and Q&A
8. Integration rules

## 1. Priority Order

Use this order when rules compete:

`scientific validity → evidence traceability → argument clarity → legibility → aesthetics`

A beautiful slide with an unsupported claim fails. A rigorous slide that cannot be read also fails.

## 2. Argument Architecture

Make one defensible main argument. Move secondary stories, complete procedural detail, and extra figures to backup.

Use the route's scientific logic:

- **Proposal:** established knowledge → bounded gap → central hypothesis/question → aims and tests → feasibility/decision rules → risks/alternatives → impact.
- **Journal club:** minimum context → claimed gap → authors' question → design → evidence sequence → alternative explanations → field comparison → calibrated verdict.

Use situation–complication–resolution or funnel–answer only as communication frames; never let them override the route's evidence requirements. Answer-first may suit senior or time-constrained audiences, but a proposal must not present predicted results as observed.

State the central question, hypothesis, or verdict by slide 2 or 3. The title slide may count when it states the question precisely.

## 3. Action Titles and Ghost Deck

An action title is a complete sentence stating the evidence-bounded takeaway:

- Weak: `Results`
- Better: `Knockdown reduces invasion without changing viability`
- Weak: `Methods`
- Better: `A rescue design separates circRNA effects from the host transcript`

Use a precise question when the answer is intentionally unresolved:

- `Does the phenotype persist after controlling for proliferation?`

Keep titles to one or two lines. Do not force certainty into background, method, proposal, or evidence-gap slides. Status words such as `PROPOSED` or `EVIDENCE_GAP` must remain visible when they affect interpretation.

Run the ghost-deck test before layout and after rendering:

1. Read only the action titles.
2. Confirm they express one coherent argument.
3. Confirm each title is supported by that slide's Claim IDs.
4. Confirm every transition makes the next slide necessary.
5. Remove or move any slide whose title can appear anywhere without changing the argument.

## 4. Exhibit Discipline

Use one dominant exhibit per content slide. Several panels are allowed when they form one comparison, experiment, or inference; otherwise split them.

Every exhibit must:

- directly support the action title;
- show the decisive observation without requiring a visual search;
- include a direct annotation, highlight, or label explaining the “so what”;
- retain controls, axes, uncertainty, and attribution needed for honest interpretation;
- be discussed in the talk, or move to backup.

Apply two tests:

- **Cover-title test:** the exhibit should still make its key pattern apparent.
- **Cover-exhibit test:** the title should be a claim that genuinely requires evidence, not a generic slogan.

Prefer graphs for trends and comparisons; use tables when exact values are the scientific point. Choose the reading order that fits the exhibit. Evidence-left/interpretation-right is useful, not mandatory.

## 5. Visual Defaults

Unless an institutional template or accessibility need says otherwise:

- use 16:9;
- use white or very light content backgrounds;
- use one sans-serif family: Arial/Helvetica for English and Heiti/YaHei or a compatible sans-serif for Chinese;
- use no more than three semantic colors;
- reserve color for meaning and emphasis, not decoration;
- use at least 0.5-inch equivalent margins and a consistent grid;
- left-align body text;
- avoid decorative icons, clip art, gradients, shadows, and full-bleed content backgrounds.

Suggested 16:9 size ranges:

| Element | Default | Floor |
|---|---:|---:|
| Action title | 28–34 pt | 24 pt |
| Short title/section statement | 36–44 pt | 30 pt |
| Body text | 20–24 pt | 20 pt |
| Figure label/annotation | 16–18 pt | 16 pt |
| Citation | 11–14 pt | 11 pt |

Increase sizes for large rooms. Treat more than roughly 40 body-text words as a warning to split, simplify, or move content to notes/backup.

## 6. Core Slide Patterns

- **Title:** scientific question or bounded claim; author, affiliation, venue, date.
- **Context/gap:** evidence for what is established beside the unresolved complication.
- **Question/hypothesis:** a dedicated anchor slide when the audience needs orientation.
- **Method/design:** only choices needed to evaluate the inference; show intervention, comparator, control, readout, and decision rule.
- **Evidence/result:** dominant exhibit, direct annotation, bounded interpretation, limitation, source.
- **Discussion:** connect evidence to the opening question and expose the most consequential alternative explanation.
- **Conclusion/Q&A:** answer the opening question with 2–4 calibrated takeaways; keep this slide visible during discussion.
- **References/backup:** place after the main narrative; make full citations and anticipated answers easy to navigate without replacing the visible conclusion during Q&A.

For long decks, prefer a compact breadcrumb or a divider that states the next scientific question. Never use a decorative section divider with no informational value.

## 7. Timing and Q&A

Use one slide per minute only as a ceiling heuristic. Complex evidence needs more time.

- rehearse to finish before the hard limit;
- target roughly 5–10% under the hard talk limit—at least 30 seconds, and usually 1–2 minutes for a 15–20 minute talk;
- predefine slides that may be skipped;
- never skip the central question, decisive evidence, or conclusion;
- prepare backup slides for the 3–5 most likely expert objections;
- end the spoken narrative while the conclusion/Q&A slide is already visible.

## 8. Integration Rules

This reference contributes communication and layout discipline. The parent skill's evidence statuses, claim ledger, full-text reading rules, figure-transformation log, route-specific scientific checks, and quality gates take precedence.

Do not copy example numbers, claims, or code from design references into a scientific deck. Use the available Codex `Presentations` or `pptx` skill for implementation and rendering.

This reference adapts selected principles from `Gabberflast/academic-pptx-skill` under the MIT License. See `third-party-notices.md`.
