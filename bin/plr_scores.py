"""
plr_scores.py

Standalone helper: returns a list of Phenotype LR (PLR) scores, one per
disease entry, from a results JSON file (e.g. LIRICAL output).

Usage:
    python plr_scores.py results.json
    python plr_scores.py results.json HP:0001250 HP:0002353   # only count matching HPO terms
"""

import json
import re
import sys

SCORE_PATTERN = re.compile(r"\[([+-]?\d+(?:\.\d+)?)\]")


def _find_disease_entries(data):
    """Yield every dict in the JSON that has 'observedPhenotypicFeatures'."""
    if isinstance(data, dict):
        if "observedPhenotypicFeatures" in data:
            yield data
        for value in data.values():
            yield from _find_disease_entries(value)
    elif isinstance(data, list):
        for item in data:
            yield from _find_disease_entries(item)


def get_plr_scores(json_path, hpo_terms=None):
    """
    Returns a list of PLR scores (sum of positive bracketed scores in each
    phenotype explanation), one per disease entry in the JSON file.

    If hpo_terms is given, only phenotypes whose explanation mentions one of
    those terms are counted. If None/empty, all phenotypes are counted.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    scores = []
    for disease_entry in _find_disease_entries(data):
        features = disease_entry.get("observedPhenotypicFeatures") or []
        # Skip plain lists of HPO IDs (e.g. the patient's input phenotypes);
        # only per-disease results have dict entries with an 'explanation'.
        features = [p for p in features if isinstance(p, dict)]
        if not features:
            continue

        phenotype_lr = 0.0
        for phenotype in features:
            explanation = str(phenotype.get("explanation", ""))
            if hpo_terms and not any(term in explanation for term in hpo_terms):
                continue
            for value in SCORE_PATTERN.findall(explanation):
                sub_lr = float(value)
                if sub_lr >= 0:
                    phenotype_lr += sub_lr
        scores.append(phenotype_lr)
    return scores


def main():
    if len(sys.argv) < 2:
        print("Usage: python plr_scores.py <results.json> [HPO_TERM ...]")
        sys.exit(1)

    json_path = sys.argv[1]
    hpo_terms = sys.argv[2:] or None

    scores = get_plr_scores(json_path, hpo_terms)
    print(f"Found {len(scores)} disease entries")
    print(scores)


if __name__ == "__main__":
    main()
