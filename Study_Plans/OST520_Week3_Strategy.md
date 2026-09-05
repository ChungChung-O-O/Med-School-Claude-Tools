# OST 520 Week 3 Study Strategy

**Status:** Ready for source processing once the Week 3 input folder is final  
**Baseline:** Unit Exam 1, 77/95 (81.1%); class average 77.6%  
**Next evidence checkpoint:** In-person exam review on Tuesday, September 8, 2026

## What the score means

Austin reported good content confidence, and his result was above the reported class average. That supports retaining the parts that felt effective, but one result does not establish how much of the score the system caused. The current working hypothesis is narrower: practice was easier and more recall-oriented than the exam, so knowledge did not always transfer cleanly into unfamiliar symptom, laboratory, and mechanism-based presentations.

This remains a hypothesis until the Tuesday review. The plan therefore adds application pressure now without rebuilding the entire study system, then uses the reviewed exam misses to decide what deserves a larger change.

## Keep from the prior strategy

1. Use course objectives and faculty materials as the coverage boundary.
2. Build concise, objective-organized learning artifacts before adding supplemental detail.
3. Keep all Anki cards in the `MedSchool` home deck with course, system, source, yield, boards, document, and exam tags.
4. Use blind questions with no topic preview, answer leak, signature buzzword, or visible build process.
5. Track wrong answers and correct-but-uncertain answers separately from confident correct answers.
6. Repair a miss with a one-sentence rule and a delayed transfer question instead of rereading a whole lecture.
7. Use mixed cumulative practice and a realistic mock before the exam.
8. Stop adding broad new material once performance is stable; the final pass should be targeted and calm.

## Add for Week 3: the application layer

### 1. Build a mechanism-to-presentation map

For every disease, deficiency, organism, immune defect, tissue abnormality, or metabolic perturbation that the course expects Austin to recognize, capture this chain:

`cause or defect -> disrupted process -> physiologic consequence -> symptom/sign/lab pattern -> closest alternative -> decisive discriminator`

The study guide should not merely list symptoms. It should explain why each major symptom or laboratory finding follows from the mechanism. If the faculty material does not support a clinical extension, mark the extension as supplemental rather than implying it is course-derived.

### 2. Use four levels of questions

The Week 3 bank should use this provisional target mix:

| Level | Target | Purpose |
|---|---:|---|
| Direct recall | 15% | Essential vocabulary, enzymes, structures, organisms, and definitions |
| Mechanism/prediction | 25% | Predict what rises, falls, fails, or remains intact after a perturbation |
| Presentation/application | 40% | Infer a mechanism, diagnosis, organism, or pathway from symptoms, signs, timing, exposures, and labs |
| Discrimination/novel transfer | 20% | Separate close alternatives or apply the same rule in a new context |

This yields 85% beyond direct recall and 60% in presentation/application or discrimination/transfer. These are planning targets, not a proven optimum. Recall cards can remain in Anki; the question bank should carry most of the application burden.

### 3. Design symptom-based items from causal chains

Each application item should contain only clues that a student could reasonably interpret from the taught mechanism. Item writers should:

- Make the decisive clue inferable but not synonymous with the answer.
- Prefer a short cluster of moderate clues over one pathognomonic giveaway.
- Use plausible distractors from the same category and explain the single feature that defeats the closest one.
- Test a downstream consequence when the mechanism is taught, such as a lab change, tissue vulnerability, host-defense failure, acid-base response, or substrate/product shift.
- Include negative findings only when they genuinely discriminate.
- Avoid teaching obscure clinical trivia that the course did not establish.

Application is not limited to symptom vignettes. Week 3 practice should also use images, experimental perturbations, pathway diagrams, graphs, and calculations when those formats match the objective.

### 4. Use a two-step response habit

For each practice question, Austin should state or think:

1. **What is the stem testing?** Name the process, category, or decision before choosing.
2. **What clue decides it?** Identify the finding that makes the chosen answer better than the closest distractor.

After grading, classify the attempt as:

- `knowledge`: the necessary fact or mechanism was absent
- `translation`: knew the fact but did not connect it to the presentation
- `discrimination`: confused two plausible alternatives
- `stem-reading`: overlooked or misweighted a clue
- `execution`: changed a supported answer, rushed, or ran out of time
- `item-quality`: ambiguous, unsupported, answer-cued, or internally inconsistent

Correct-but-uncertain answers still enter the repair queue.

## Processing workflow when the input folder is ready

### Phase A: inventory and source control

1. Treat `/Users/austin_cheng/Desktop/MSUCOM/26 Fall/OST 520/_inputs/Week 3 Biomedical Science/` as the source set for this run.
2. Inventory every file and identify duplicate formats of the same lecture. Prefer outlines for exact objectives and slides for figures or emphasis; do not count duplicate formats as separate coverage.
3. Identify the authoritative objectives or stated learning goals for every lecture. Flag any lecture with no recoverable objectives before generating content.
4. Record a manifest with lecture number, title, faculty, source files, objective count, and processing status.

### Phase B: course-grounded learning artifacts

For each lecture or reading review:

1. Extract objectives, named concepts, emphasized comparisons, faculty practice items, and figure-dependent content.
2. Produce a concise objective-by-objective guide.
3. Add a `Mechanism -> Presentation` section where clinically relevant.
4. Add a `Closest Confusions` table for easily mixed concepts.
5. Create Anki cards only for durable facts, short causal links, and discriminators. Do not turn full vignettes into bloated cards.
6. For histology, cell identification, pathway diagrams, graphs, or calculations, retain the necessary visual or data stimulus and create interpretation questions. A prose vignette does not replace an image-identification objective. Record unavailable essential figures as explicit coverage gaps.

### Phase C: Week 3 question-bank expansion

1. Confirm the Week 3 unit assignment against the course schedule before assigning an existing unit code such as `UE2`.
2. Add Week 3 material to the correct OST 520 unit shelf while preserving all Unit 1 progress and identifiers.
3. Give every question stable metadata: course, unit, lecture/objective coverage, concept tags, source reference, difficulty/application level, and closest-confusion family when applicable.
4. Create a small same-day application set per lecture, a cumulative mixed set after several lectures, and a later full mock.
5. Reserve an unseen cumulative set before daily practice begins. Holdout questions must use different presentations from taught examples and repair questions. Report first-attempt unseen accuracy separately from repeat accuracy; once used, a holdout item becomes ordinary practice material.
6. Keep faculty-authored practice items identifiable and separate from newly written bank questions.
7. Preserve answer keys outside blind practice surfaces.
8. Treat `index.html` as the current question-bank source of truth, regenerate `bank.json`, and verify data equivalence. Map any new error categories or application metadata explicitly to existing attempt fields, preserving historical labels and backup compatibility.

### Phase D: quality gate

Before release, verify:

- Every objective is represented in the guide and retrieval system.
- Every major application objective has at least two meaningfully different retrieval opportunities where the sources support them. Choose the format that fits the objective: symptom presentation, prediction, comparison, image interpretation, or calculation.
- The scored question mix is approximately 15% recall, 25% mechanism/prediction, 40% presentation/application, and 20% discrimination/transfer.
- Figure-dependent objectives retain their image or data stimulus; unavailable essential figures are reported as coverage gaps.
- No answer is exposed by topic labels, file names, processing commentary, signature wording, option length, or formatting.
- Distractors are parallel and plausible, with a documented closest distractor.
- Rationales explain the causal chain and why the closest alternative fails.
- Supplemental claims are marked and medically checked.
- Existing Unit 1 questions, progress formats, backups, and analytics remain compatible.
- Automated integrity and quality tests pass, followed by a browser-level user-flow check.

## Daily operating loop

1. **Learn:** Work through the objective-organized source guide.
2. **Retrieve:** Do the associated Anki cards closed-book.
3. **Translate:** Complete 8-12 blind application questions from that day’s material.
4. **Explain:** For every miss or uncertain answer, state the causal chain and decisive clue aloud.
5. **Transfer:** Re-test the same concept later with a different presentation, not the same wording.
6. **Mix:** End with 5-10 questions from older Week 3 material so early lectures stay alive.

Once enough material is available, use one cumulative mixed block every 2-3 days. Its purpose is to force topic identification without a lecture label.

This loop replaces the site's default `Today's adaptive 40` when followed; it is not additional required work. Use one daily question budget that includes new application, repair, and cumulative items. Start with 13-22 questions from the loop above, measure the real time required, and adjust using delayed performance rather than allowing the workload to double silently.

## Tuesday exam-review protocol

Do not try to memorize or reproduce protected exam wording. For each reviewed miss, capture only:

| Field | What to record |
|---|---|
| Concept | The tested idea in general terms |
| Your reasoning | Why your selected answer seemed right |
| Decisive clue | The clue or relationship you missed or misweighted |
| Error type | Knowledge, translation, discrimination, stem-reading, execution, or item-quality |
| Corrected rule | One sentence that would solve a new version |
| Transfer target | What a different presentation of the same idea could look like |

Assign one primary error cause, an optional secondary cause, and allow `uncertain` when the cause cannot be determined. Separate defects in our practice items from disputed or unclear exam items. Prioritize recurring, well-supported patterns rather than forcing every miss into a category.

Also record correct questions that felt like guesses. Immediately after the in-person session, produce a debrief while the reasoning is fresh. Then update this plan based on the pattern:

- Mostly `knowledge` -> strengthen objective coverage and selective Anki.
- Mostly `translation` -> increase mechanism-to-symptom chains and presentation questions.
- Mostly `discrimination` -> build paired comparison sets and closest-distractor drills.
- Mostly `stem-reading` or `execution` -> add timed blocks and explicit clue-selection habits.
- Repeated `item-quality` findings in our own bank -> report and quarantine those practice items rather than training on them. Keep disputed exam items in a separate review note.

## Success measures for the next exam cycle

The next cycle is working if:

1. Presentation/application plus discrimination/transfer questions reach approximately 60% of the scored bank without sacrificing objective coverage; 85% should require more than direct recall.
2. On a small sampled portion of unseen mixed questions, Austin identifies the decisive clue before viewing the rationale. Track whether the explanation supports the answer and use 80% only as a provisional target after establishing a baseline.
3. Correct-but-uncertain answers and translation errors decrease across delayed retests.
4. A final mixed mock is closer in difficulty and presentation style to the real exam than the prior mock.
5. The Tuesday debrief shows that the revised system targets the actual miss pattern rather than the current hypothesis alone.

## Current launch condition

Do not begin the full build until Austin confirms the Week 3 download is complete. At launch, re-inventory the input folder because files may have been added or replaced after this plan was written.
