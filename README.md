# Incomplete Penetrance Functions

## Overview

This repo is a collection of standalone Python scripts for working with patient phenotype data and HPO (Human Phenotype Ontology) based diagnostic results. Each script lives in `bin/` and can be run on its own.

| Script | What it does | Example input |
| --- | --- | --- |
| `nodeFinder.py` | Finds patient JSON files that contain highly similar HPO terms | `examples/patient1.json`, `examples/patient2.json` |
| `plr_scores.py` | Returns a list of Phenotype LR (PLR) scores, one per disease entry, from a results JSON | `examples/output1.json` |

---

## Repository organization

```text
project-name/
├── bin/
│   ├── nodeFinder.py
│   └── plr_scores.py
├── examples/
│   ├── patient1.json
│   ├── patient2.json
│   └── output1.json
├── DOCUMENTATION.md
└── README.md
```

---

## Requirements

All scripts require Python 3.

Standard libraries used across the scripts:

```text
json
os
re
sys
itertools
functools
```

External packages (needed for `nodeFinder.py`):

```text
networkx
obonet
```

To install them, run:

```bash
pip install networkx obonet
```

`plr_scores.py` uses only the standard library.

---

## Functions

### 1. `nodeFinder.py`: similar HPO term finder

Extracts HPO IDs from patient JSON files, compares the terms using the HPO graph, and prints the filenames that contain at least one pair of closely related terms.

**Run:**

```bash
python bin/nodeFinder.py examples
```

**Similarity definition:** two HPO terms are considered similar if their shortest-path distance in the HPO graph is 2 or less. This cutoff is used to flag phenotype terms that may be closely related or redundant.

**Notes:**

* Reads the Human Phenotype Ontology from an online `.obo` file using `obonet`, so it needs an internet connection.
* Only prints the filenames that contain similar HPO terms.

---

### 2. `plr_scores.py`: Phenotype LR scores

Reads a results JSON (e.g. LIRICAL output) and returns a list of PLR scores, one per disease entry. Each score is the sum of the positive bracketed scores in that disease's `observedPhenotypicFeatures` explanations.

**Run:**

```bash
python bin/plr_scores.py examples/output1.json
```

**Use from other code:**

```python
from plr_scores import get_plr_scores

scores = get_plr_scores("examples/output1.json")
```
---

See `DOCUMENTATION.md` for a more detailed explanation of each script and its functions.
