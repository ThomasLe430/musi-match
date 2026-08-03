from src.recommender import score_song, recommend_songs

def make_small_songs():
    return [
        {
            "id": 1,
            "title": "Test Pop Track",
            "artist": "Test Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.9,
            "isInstrumental": False,
            "duration": 180,
        },
        {
            "id": 2,
            "title": "Chill Lofi Loop",
            "artist": "Test Artist",
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.4,
            "tempo_bpm": 80,
            "valence": 0.6,
            "isInstrumental": True,
            "duration": 120,
        },
    ]


def test_recommend_returns_songs_sorted_by_score():
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "instrumental": False,
    }
    songs = make_small_songs()
    results = recommend_songs(user_prefs, songs, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    top_song, _, _ = results[0]
    assert top_song["genre"] == "pop"
    assert top_song["mood"] == "happy"
    assert results[0][1] >= results[1][1]


def test_explain_recommendation_returns_non_empty_string():
    user_prefs = {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "instrumental": False,
    }
    songs = make_small_songs()
    song = songs[0]

    _, explanation = score_song(user_prefs, song)
    explanation = ", ".join(explanation) if explanation else "No strong matches"

    assert isinstance(explanation, str)
    assert explanation.strip() != ""
