import csv
from typing import List, Dict, Tuple, Optional

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "isInstrumental": row["isInstrumental"].strip().lower() == "true",
                "duration": int(row["duration"]),
            })
    return songs

# Weight given to each preference when scoring a song. Genre and mood are
# weighted highest since "vibe" match matters most for a simple recommender;
# weights sum to 1.0 so a song matching every preference scores exactly 1.0.
SCORE_WEIGHTS = {
    "genre": 0.30,
    "mood": 0.30,
    "artist": 0.10,
    "energy": 0.10,
    "valence": 0.08,
    "tempo_bpm": 0.05,
    "instrumental": 0.02,
    "duration": 0.05,
}

# Spans used to normalize numerical distances onto a 0-1 scale before the
# inverse-distance calculation (energy/valence are already 0-1).
NUMERICAL_RANGES = {
    "energy": 1.0,
    "valence": 1.0,
    "tempo_bpm": 115.0, # Hard coded as the max(bpm) - min(bpm) in songs.csv
    "duration": 153.0, # Hard coded as the max(duration) - min(duration) in songs.csv
}

# If numerical features are scored above 0.7 --> Feature added
# to explanation list
NUMERICAL_PREF_THRESHOLD = 0.7

# Short display labels for numerical features in explanations.
NUMERICAL_LABELS = {
    "energy": "Energy",
    "valence": "Valence",
    "tempo_bpm": "Tempo",
    "duration": "Duration",
}

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Preferences the user didn't specify (missing from user_prefs, or
    missing from the song's data) are excluded from scoring entirely
    rather than counted as unsatisfied: the raw score is renormalized by
    the total weight of only the preferences actually evaluated, so a
    user who skips a preference can still reach a max score of 1.0.
    """
    score = 0.0
    specified_weight = 0.0
    reasons: List[str] = []

    # --- Categorical features: equality/existence checks ---
    for key, label in (("genre", "genre"), ("mood", "mood"), ("artist", "artist")):
        pref = user_prefs.get(key)
        value = song.get(key)
        if not pref or value is None:
            continue
        specified_weight += SCORE_WEIGHTS[key]
        wanted = pref if isinstance(pref, (list, tuple, set)) else [pref]
        wanted = {str(w).strip().lower() for w in wanted}
        if str(value).strip().lower() in wanted:
            score += SCORE_WEIGHTS[key]
            reasons.append(f"{label.capitalize()}: {value}")

    # Check instrumental preferences
    instrumental_pref = user_prefs.get("instrumental")
    song_instrumental = song.get("isInstrumental", song.get("is_instrumental"))
    if instrumental_pref is not None and song_instrumental is not None:
        specified_weight += SCORE_WEIGHTS["instrumental"]
        if bool(song_instrumental) == bool(instrumental_pref):
            score += SCORE_WEIGHTS["instrumental"]
            reasons.append("Instrumental match")

    # --- Numerical features: inverse distance from target ---
    for key in ("energy", "valence", "tempo_bpm", "duration"):
        target = user_prefs.get(key)
        value = song.get(key)
        if target is None or value is None:
            continue
        specified_weight += SCORE_WEIGHTS[key]
        closeness = max(0.0, 1.0 - abs(float(value) - float(target)) / NUMERICAL_RANGES[key])
        score += SCORE_WEIGHTS[key] * closeness
        if closeness >= NUMERICAL_PREF_THRESHOLD:
            reasons.append(f"{NUMERICAL_LABELS[key]} match")

    # Ensure no divide by zero
    if specified_weight == 0:
        return 0.0, reasons

    return round(min(score / specified_weight, 1.0), 4), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "No strong matches"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]

# TODO: Implement text_to_profile
def text_to_profile(desc: str):
    '''
    Takes in a user's description of the song profile they have in mind
    Text profile --> Converted to a UserProfile compatible with score_song
    '''
