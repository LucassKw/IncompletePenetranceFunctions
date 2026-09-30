# Documentation

This file explains each script in `bin/` in more detail: what it does, its input and output, and how each function inside it works. See `README.md` for a quick overview and run commands.

## Contents

1. [`nodeFinder.py`](#1-nodefinderpy): similar HPO term finder
2. [`plr_scores.py`](#2-plr_scorespy): Phenotype LR scores

---

## 1. `nodeFinder.py`

### Purpose

Checks patient JSON files for highly similar Human Phenotype Ontology (HPO) terms.

It reads each `.json` file in a folder, extracts the HPO IDs from the `phenotypicFeatures` section, and compares every pair of HPO terms within each file. If any two HPO terms are within a shortest-path distance of 2 or less in the HPO graph, the file is flagged as containing similar phenotype terms.

### Input

One command-line argument: a folder of JSON files.

```bash
python bin/nodeFinder.py path/to/json_folder
```

Each JSON file is expected to have a `phenotypicFeatures` list where each item has a `type` with an `id`, for example:

```json
{
  "phenotypicFeatures": [
    { "type": { "id": "HP:0001250", "label": "Seizure" } }
  ]
}
```

Files without `phenotypicFeatures` are skipped (they have no terms to compare, so they are never flagged).

### Output

A printed Python list of JSON filenames that contain at least one pair of similar HPO terms, for example:

```text
['patient1.json']
```

### How it works

On startup, the script downloads the HPO ontology from `http://purl.obolibrary.org/obo/hp.obo` with `obonet` and converts it to an undirected `networkx` graph. Treating the graph as undirected means distance counts steps in either direction, so parent, child and sibling terms are all close to each other.

### Functions

**`pheno_ids(json_file)`**
Opens one JSON file and returns a list of the HPO IDs in its `phenotypicFeatures` section. IDs that are not in the HPO graph are ignored.

**`shortest_paths_from(source)`**
Returns the shortest-path distance from one HPO term to every other term in the graph. Results are cached with `lru_cache`, so each term's distances are only computed once, even across many files.

**`sim_check(term_ids)`**
Builds every pair of terms in the list and looks up their distance. Returns `True` as soon as it finds a pair with a distance of 2 or less, and `False` otherwise.

**`run_folder(json_folder)`**
Runs `pheno_ids` and `sim_check` on every `.json` file in the folder and prints the list of flagged filenames.

### Similarity definition

Two HPO terms are similar if their shortest-path distance in the HPO graph is 2 or less. A distance of 1 means one term is the direct parent of the other; a distance of 2 covers grandparents and siblings (terms that share a parent). This cutoff flags terms that may be closely related or redundant.

### Notes

* Needs an internet connection, since the ontology is downloaded each time the script runs.
* A file with fewer than two valid HPO terms can never be flagged.

---

## 2. `plr_scores.py`

### Purpose

Reads a diagnostic results JSON (e.g. LIRICAL output) and returns a list of Phenotype Likelihood Ratio (PLR) scores, one per disease entry.

### Input

A results JSON file.

```bash
python bin/plr_scores.py examples/Output1.json
```

The script looks for disease entries with an `observedPhenotypicFeatures` list, where each phenotype has an `explanation` string containing scores in square brackets, for example `[1.221]`. In LIRICAL output these entries are under `analysisResults`.

The patient's own input phenotypes (in `analysisData`) also use the key `observedPhenotypicFeatures`, but as a plain list of HPO IDs. These are skipped, so they don't add extra scores to the list.

### Output

The number of disease entries found, followed by the list of PLR scores in the same order as the entries appear in the file. For `examples/Output1.json`:

```text
Found 3 disease entries
[0.0, 1.699, 1.221]
```

(The printed values may show small floating-point rounding, e.g. `1.6989999999999998`.)

### How a PLR score is calculated

For each disease entry:

1. Go through each phenotype in `observedPhenotypicFeatures`.
2. Pull out every number in square brackets from the explanation.
3. Add up the numbers that are 0 or greater. Negative numbers are ignored.

The total is that disease's PLR score.

### Functions

**`get_plr_scores(json_path)`**
Main function. Opens the JSON file and returns the list of PLR scores. Can be imported and used from other scripts:

```python
from plr_scores import get_plr_scores

scores = get_plr_scores("examples/Output1.json")
```

**`_find_disease_entries(data)`**
Helper that searches the whole JSON, at any depth, and yields every object that has an `observedPhenotypicFeatures` key. This means the script doesn't depend on the exact layout of the file.

**`main()`**
Reads the file path from the command line, calls `get_plr_scores`, and prints the result. Prints a usage message if no file is given.

### Notes

* Uses only the Python standard library.
* A malformed or unreadable JSON file raises an error, rather than silently returning zero scores.
