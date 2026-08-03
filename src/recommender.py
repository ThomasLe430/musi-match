import csv
import json
import os
from typing import List, Dict, Tuple, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

# Vocabulary present in data/songs.csv. Grounding the LLM on these lets it map
# free text onto values that will actually equality-match in score_song,
# instead of inventing synonyms (e.g. "chilled out" -> "chill").
# Sourced from the Kaggle Spotify dataset's track_genre values (normalized in
# src/transform_kaggle_data.py). Every entry here has at least one matching
# song in songs.csv.
KNOWN_GENRES = [
    "acoustic", "afrobeat", "alt-rock", "alternative", "ambient", "anime",
    "black-metal", "bluegrass", "blues", "brazil", "breakbeat", "british",
    "cantopop", "chicago-house", "children", "chill", "classical", "club",
    "comedy", "country", "dance", "dancehall", "death-metal", "deep-house",
    "detroit-techno", "disco", "disney", "drum-and-bass", "dub", "dubstep",
    "edm", "electro", "electronic", "emo", "folk", "forro", "french", "funk",
    "garage", "german", "gospel", "goth", "grindcore", "groove", "grunge",
    "guitar", "happy", "hard-rock", "hardcore", "hardstyle", "heavy-metal",
    "hip-hop", "honky-tonk", "house", "idm", "indian", "indie", "indie pop",
    "industrial", "iranian", "j-dance", "j-idol", "j-pop", "j-rock", "jazz",
    "k-pop", "kids", "latin", "latino", "malay", "mandopop", "metal",
    "metalcore", "minimal-techno", "mpb", "new-age", "opera", "pagode",
    "party", "piano", "pop", "power-pop", "progressive-house", "psych-rock",
    "punk", "punk-rock", "r&b", "reggae", "reggaeton", "rock", "rock-n-roll",
    "rockabilly", "romance", "sad", "salsa", "samba", "sertanejo",
    "show-tunes", "singer-songwriter", "ska", "sleep", "soul", "spanish",
    "study", "swedish", "synth-pop", "tango", "techno", "trance",
    "trip-hop", "turkish", "world",
]
# Sourced from the mood grid derived in src/transform_kaggle_data.py
# (valence x energy tertile buckets), which is the only place moods come
# from now since Kaggle has no mood column.
KNOWN_MOODS = [
    "happy", "chill", "intense", "energetic", "melancholic", "peaceful",
    "relaxed", "moody",
]

PROFILE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "artist": {"type": "STRING", "nullable": True},
        "genre": {"type": "ARRAY", "items": {"type": "STRING"}, "nullable": True},
        "mood": {"type": "ARRAY", "items": {"type": "STRING"}, "nullable": True},
        "energy": {"type": "NUMBER", "nullable": True},
        "valence": {"type": "NUMBER", "nullable": True},
        "instrumental": {"type": "BOOLEAN", "nullable": True},
        "tempo_bpm": {"type": "INTEGER", "nullable": True},
        "duration": {"type": "INTEGER", "nullable": True},
    },
    "required": ["artist", "genre", "mood", "energy", "valence", "instrumental", "tempo_bpm", "duration"],
}

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
    "tempo_bpm": 243.0, # Hard coded as the max(bpm) - min(bpm) in songs.csv
    "duration": 5228.0, # Hard coded as the max(duration) - min(duration) in songs.csv
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

def _clamp01(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return max(0.0, min(1.0, float(value)))


def text_to_profile(desc: str) -> Dict:
    '''
    Takes in a user's description of the song profile they have in mind
    Text profile --> Converted to a user profile dict compatible with score_song
    Required by retrieve_candidates
    '''
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set")

    prompt = (
        "Extract a music preference profile from this description:\n"
        f'"{desc}"\n\n'
        f"Known genres (prefer these when the description matches): {', '.join(KNOWN_GENRES)}\n"
        f"Known moods (prefer these when the description matches): {', '.join(KNOWN_MOODS)}\n\n"
        "energy and valence are floats from 0 (low) to 1 (high). "
        "tempo_bpm is an integer beats-per-minute estimate. "
        "duration is an integer number of seconds. "
        "Set a field to null if the description gives no signal for it."
    )

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PROFILE_SCHEMA,
        ),
    )
    raw = json.loads(response.text)

    return {
        "artist": raw.get("artist"),
        "genre": raw.get("genre"),
        "mood": raw.get("mood"),
        "energy": _clamp01(raw.get("energy")),
        "valence": _clamp01(raw.get("valence")),
        "instrumental": raw.get("instrumental"),
        "tempo_bpm": int(raw["tempo_bpm"]) if raw.get("tempo_bpm") is not None else None,
        "duration": int(raw["duration"]) if raw.get("duration") is not None else None,
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
    Required by generate_explanation() and src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons) if reasons else "No strong matches"
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]

# TODO: Implement
def generate_explanation(songs: List[Tuple[Dict, float, str]]):
    '''
    LLM call to create a friendly explanation of the songs recommendation
    '''
    pass
