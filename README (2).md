# LaTeX Proof Analyzer

A tool that analyzes mathematical proofs written in LaTeX to identify:
- Logical steps and their dependencies
- Assumptions and their scope (global vs local)
- Potential gaps (undefined symbols, uncited theorems, unassumed properties, "obvious" leaps)
- A visual dependency graph

## Installation

```bash
pip install gradio networkx
# Also requires graphviz system package for graph rendering
# Ubuntu/Debian: apt-get install graphviz
# macOS: brew install graphviz
```

## Usage

### Run the Gradio Web UI

```bash
python app.py
```

Then open http://localhost:7860 in your browser.

### Use Programmatically

```python
from pipeline import analyze_proof, format_results_as_dict

latex_proof = r"""
Let $G$ be a finite group. We claim that...
"""

result = analyze_proof(latex_proof)
data = format_results_as_dict(result)

print(f"Steps: {len(data['steps'])}")
print(f"Assumptions: {len(data['assumptions'])}")
print(f"Flags: {len(data['flags'])}")
```

## Architecture

```
proof-analyzer/
├── app.py                    # Gradio UI
├── pipeline.py               # Main orchestrator
├── demo_proofs.py            # Example proofs for testing
└── modules/
    ├── models.py             # Data classes (Step, Assumption, Flag)
    ├── preprocessor.py       # LaTeX cleanup and normalization
    ├── segmenter.py          # Split proof into logical steps
    ├── token_extractor.py    # Extract math symbols and tokens
    ├── assumption_extractor.py # Detect assumptions and scope
    ├── gap_detector.py       # Heuristic gap detection
    └── graph_builder.py      # Dependency graph construction
```

## Gap Detection Heuristics

1. **Undefined Symbol**: Token appears multiple times but never introduced via Let/Define/Assume
2. **Uncited Theorem**: "by theorem/lemma" without number/reference (excludes "by definition", "by construction", etc.)
3. **Unassumed Property**: Property like "compact" used in reasoning but not established
4. **Obvious Leap**: "clearly/obviously" on complex expressions (multiple operators, long text)

## Improvements Over Original Plan

- **Better segmentation**: Avoids splitting inside math mode, handles abbreviations
- **Better token extraction**: Handles Greek letters, \mathbb, \mathcal, operator names
- **Improved scope detection**: Uses first-claim heuristic instead of arbitrary "first N steps"
- **Expanded property list**: 100+ mathematical properties across multiple domains
- **Reduced false positives**: Standard phrases excluded from "uncited theorem" check
- **Error handling**: Graceful handling of malformed LaTeX, empty input

## Limitations

- No formal proof verification (heuristic only)
- No external theorem database lookup
- Single-proof documents only
- May produce false positives/negatives on unusual proof styles
