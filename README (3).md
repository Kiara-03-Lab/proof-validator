# Proof Analyzer (LaTeX Proof Dependency Graph)

This project reads a mathematical proof written in LaTeX and produces a **human-friendly structural analysis**:
- a list of proof **steps**
- extracted **assumptions** (global vs local)
- **heuristic warnings** about possible gaps
- a **dependency graph** showing which steps justify which later steps

This is designed to help mathematicians *read, refactor, teach, and audit* proofs. It is **not** a formal verifier.

---

## What you give it

You paste a single proof written in ordinary LaTeX prose (the kind you would put in a paper):
- “Let …” / “Assume …” / “Suppose …”
- “Then …” / “Hence …” / “Therefore …”
- “By Lemma …” / “By definition …”

Tip: If you include mathematical notation, that is fine. The analyzer focuses on structure, not correctness.

---

## What you get back

### 1) Steps
The proof is segmented into steps labeled like:
- S1, S2, S3, ...

Each step is a unit of reasoning (a claim, deduction, case split, or application of a result).

### 2) Assumptions (scope-aware)
Assumptions are extracted and labeled like:
- A1, A2, ...

They are classified as:
- **Global**: intended to hold throughout the whole proof
- **Local**: holds only inside a sub-argument (a case, contradiction block, temporary hypothesis, etc.)

### 3) Gap warnings (heuristic)
The tool flags *possible* issues, such as:
- **Undefined symbol**: used repeatedly but never introduced by “Let/Define/Assume”
- **Uncited theorem**: “by theorem/lemma” without a number or reference
- **Unassumed property**: a property like “compact”, “bounded”, “normal”, etc. is used but not stated
- **Obvious leap**: “clearly/obviously” used on a complex expression

These are prompts for review, not accusations.

### 4) Dependency graph
A directed graph visualizes dependencies between assumptions and steps.

Nodes:
- S1, S2, ... are proof steps
- A1, A2, ... are assumptions

Edges (arrows):
- X -> Y means “X is used to justify Y”

Edge weights (numbers on arrows):
- 1.0 means strong/direct dependence
- smaller values mean weaker/indirect influence

---

## How to read the graph (quick guide)

- Items near the top are usually early assumptions and early steps.
- Items near the bottom are later consequences and final conclusions.
- Many arrows into a step means it relies on multiple earlier facts.
- Long arrows reaching far downward mean early facts reused later.
- Tight clusters often indicate a sub-argument (a lemma-like block or a case analysis).

---

## Run the Web App (Gradio UI)

Install dependencies:

```bash
pip install gradio networkx
# Graph rendering also requires Graphviz:
# Ubuntu/Debian: apt-get install graphviz
# macOS: brew install graphviz
```

Run:

```bash
python app.py
```

Then open the URL shown in the terminal (commonly http://localhost:7860).

---

## Use as a Python library (optional)

If you (or a collaborator) wants programmatic access:

```python
from pipeline import analyze_proof, format_results_as_dict

latex_proof = """
Let G be a finite group. We claim that ...
"""

result = analyze_proof(latex_proof)
data = format_results_as_dict(result)

print("Steps:", len(data["steps"]))
print("Assumptions:", len(data["assumptions"]))
print("Flags:", len(data["flags"]))
```

---

## Project layout

- app.py: Gradio web UI
- pipeline.py: main orchestrator
- demo_proofs.py: example inputs
- modules/: implementation modules
  - models.py: data classes (Step, Assumption, Flag)
  - preprocessor.py: LaTeX cleanup/normalization
  - segmenter.py: splits proof into steps
  - token_extractor.py: extracts symbols/tokens
  - assumption_extractor.py: detects assumptions and scope
  - gap_detector.py: heuristic gap detection
  - graph_builder.py: builds the dependency graph

---

## Limitations

- Heuristic analysis only (no formal proof checking)
- No external theorem database lookup
- Best suited for single-proof inputs (not entire multi-proof papers)
- May produce false positives/negatives on unusual styles

---

## Recommended workflow

1. Paste your proof and run analysis.
2. Inspect the graph to find major dependency chains and clusters.
3. Review warnings and decide which are real issues vs stylistic choices.
4. Use the output to rewrite or annotate the proof more clearly.
