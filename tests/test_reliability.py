import os

import pytest

from src.reliability import compare_profiles, check_profile_consistency
from src.recommender import text_to_profile


def test_compare_profiles_identical_is_perfect_score():
    profile = {"genre": ["lofi", "jazz"], "mood": ["chill"], "energy": 0.4, "valence": 0.6}
    scores = compare_profiles(profile, profile)

    assert scores == {"genre": 1.0, "mood": 1.0, "energy": 1.0, "valence": 1.0}


def test_compare_profiles_disjoint_genre_scores_zero():
    a = {"genre": ["rock"], "mood": ["chill"], "energy": 0.5, "valence": 0.5}
    b = {"genre": ["jazz"], "mood": ["chill"], "energy": 0.5, "valence": 0.5}
    scores = compare_profiles(a, b)

    assert scores["genre"] == 0.0
    assert scores["mood"] == 1.0


def test_compare_profiles_partial_genre_overlap_is_between_zero_and_one():
    a = {"genre": ["rock", "pop"], "mood": None, "energy": None, "valence": None}
    b = {"genre": ["pop", "jazz"], "mood": None, "energy": None, "valence": None}
    scores = compare_profiles(a, b)

    # Jaccard overlap of {rock, pop} and {pop, jazz} is 1/3
    assert scores["genre"] == pytest.approx(1 / 3)


def test_compare_profiles_numeric_distance():
    a = {"genre": None, "mood": None, "energy": 0.8, "valence": 0.2}
    b = {"genre": None, "mood": None, "energy": 0.5, "valence": 0.2}
    scores = compare_profiles(a, b)

    assert scores["energy"] == pytest.approx(0.7)
    assert scores["valence"] == pytest.approx(1.0)


def test_check_profile_consistency_aggregates_across_repeats():
    call_count = {"n": 0}

    def fake_text_to_profile(desc):
        call_count["n"] += 1
        return {"genre": ["lofi"], "mood": ["chill"], "energy": 0.4, "valence": 0.6}

    import src.reliability as reliability
    original = reliability.text_to_profile
    reliability.text_to_profile = fake_text_to_profile
    try:
        result = reliability.check_profile_consistency(["some description"], repeats=3)
    finally:
        reliability.text_to_profile = original

    assert call_count["n"] == 3
    assert result["overall_score"] == 1.0
    assert result["per_description"][0]["field_scores"]["genre"] == 1.0


@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="requires GEMINI_API_KEY")
def test_text_to_profile_consistency_live():
    desc = "Something chill and instrumental for studying, lofi or jazz, no strong artist preference."
    result = check_profile_consistency([desc], repeats=2)

    assert 0.0 <= result["overall_score"] <= 1.0
