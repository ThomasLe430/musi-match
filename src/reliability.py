import json
import os
from datetime import datetime, timezone
from itertools import combinations
from typing import Dict, List, Optional

try:
    from recommender import text_to_profile
except ImportError:
    from src.recommender import text_to_profile

# Paraphrases of the same underlying intent (chill/lofi/jazz, instrumental,
# slow, short, no artist preference). A reliable LLM extraction should land
# on roughly the same profile across all of them.
DEFAULT_TEST_DESCRIPTIONS = [
    "I do not care what artist, but I am in a chill mood and would love a good lofi "
    "or jazz song to do homework to. The song should be slow, short, and preferably instrumental.",
    "I'm studying and want something mellow and lo-fi or jazzy to relax to. Doesn't matter who "
    "made it, just keep it short, slow, and mostly instrumental.",
    "Any artist is fine. I want a calm, laid-back track for homework - jazz or lofi vibes, "
    "on the shorter and slower side, ideally with no vocals.",
]

REPORT_PATH = os.path.join("reports", "reliability_report.json")


def _jaccard(a, b) -> float:
    set_a = {str(x).strip().lower() for x in (a or [])}
    set_b = {str(x).strip().lower() for x in (b or [])}
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def _numeric_closeness(a: Optional[float], b: Optional[float]) -> float:
    if a is None or b is None:
        return 1.0 if a == b else 0.0
    return max(0.0, 1.0 - abs(float(a) - float(b)))


def compare_profiles(profile_a: Dict, profile_b: Dict) -> Dict[str, float]:
    """Per-field agreement between two extracted profiles, each on a 0-1 scale."""
    return {
        "genre": _jaccard(profile_a.get("genre"), profile_b.get("genre")),
        "mood": _jaccard(profile_a.get("mood"), profile_b.get("mood")),
        "energy": _numeric_closeness(profile_a.get("energy"), profile_b.get("energy")),
        "valence": _numeric_closeness(profile_a.get("valence"), profile_b.get("valence")),
    }


def check_profile_consistency(descriptions: List[str], repeats: int = 3) -> Dict:
    """
    Calls text_to_profile `repeats` times per description and measures how
    much the extracted profiles agree with each other across runs. High
    agreement means the LLM extracts a consistent structured profile for the
    same (or equivalently phrased) input.
    """
    per_description = []
    for desc in descriptions:
        profiles = [text_to_profile(desc) for _ in range(repeats)]
        pair_scores = [compare_profiles(a, b) for a, b in combinations(profiles, 2)]

        field_scores = {
            field: round(sum(p[field] for p in pair_scores) / len(pair_scores), 4)
            for field in ("genre", "mood", "energy", "valence")
        }
        overall = sum(field_scores.values()) / len(field_scores)

        per_description.append({
            "description": desc,
            "profiles": profiles,
            "field_scores": field_scores,
            "overall_score": round(overall, 4),
        })

    overall_score = sum(d["overall_score"] for d in per_description) / len(per_description)
    return {
        "repeats": repeats,
        "per_description": per_description,
        "overall_score": round(overall_score, 4),
    }


def run_reliability_report(descriptions: Optional[List[str]] = None) -> Dict:
    """
    Entry point used by `python src/main.py --check-reliability`. Measures
    text_to_profile consistency across a fixed test set, writes a JSON
    report, and prints a human-readable summary.
    """
    descriptions = descriptions or DEFAULT_TEST_DESCRIPTIONS
    results = check_profile_consistency(descriptions)
    results["generated_at"] = datetime.now(timezone.utc).isoformat()

    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    weakest = min(results["per_description"], key=lambda d: d["overall_score"])
    weakest_field = min(weakest["field_scores"], key=weakest["field_scores"].get)

    print(f"Reliability report written to {REPORT_PATH}")
    print(f"Overall consistency: {results['overall_score']:.0%}")
    print(f"Weakest description: \"{weakest['description'][:60]}...\" ({weakest['overall_score']:.0%})")
    print(f"Weakest field: {weakest_field} ({weakest['field_scores'][weakest_field]:.0%})")

    return results
