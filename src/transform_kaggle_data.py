"""
One-off ETL: converts data/KaggleSpotifyDataset.csv into the schema
load_songs() in src/recommender.py expects (see data/songs.csv).

Run once after (re)downloading the Kaggle dataset:
    python src/transform_kaggle_data.py

Steps:
  1. Drop rows with no track_name/artists (Kaggle has a handful of these).
  2. Dedupe by track_id — the Kaggle dataset samples ~1000 tracks per
     track_genre, so the same track can appear under multiple genre rows.
     We keep the first occurrence and drop the rest.
  2b. Dedupe by (title, artist) — the same song is often released on
      multiple albums/compilations under different track_ids (re-releases,
      deluxe editions, holiday compilations), which step 2 can't catch
      since each has a distinct track_id. Of each group we keep the row
      with the highest `popularity`, since that's the version listeners
      actually recognize.
  3. Map columns onto the target schema:
       track_name       -> title
       artists           -> artist (first artist only; see NOTE below)
       track_genre       -> genre (normalized, see GENRE_ALIASES)
       energy, valence   -> copied as-is (already 0-1 floats)
       tempo             -> tempo_bpm (rounded to int)
       duration_ms       -> duration (/1000, rounded to int seconds)
       instrumentalness  -> isInstrumental (thresholded at 0.5, per Spotify's
                            own docs: values above 0.5 are intended to
                            represent instrumental tracks)
       energy + valence  -> mood (derived; there's no mood column in Kaggle)
  4. Drops everything else (popularity, danceability, key, loudness, mode,
     speechiness, acousticness, liveness, time_signature, album_name,
     track_id, explicit) since score_song() never reads them.

NOTE on multi-artist tracks: Kaggle joins collaborators with ";"
(e.g. "Ingrid Michaelson;ZAYN"). score_song does an equality/membership
check against a single artist string, so keeping the full joined string
would make a user's "ZAYN" preference fail to match. We keep only the
first-listed (primary) artist to stay compatible with that check.

NOTE on mood: derived from a 3x3 grid over (valence, energy), following
the standard valence/energy "circumplex" split used for music mood
classification. This is a heuristic, not a ground-truth label — treat
it as approximate.
"""

import csv

INPUT_PATH = "data/KaggleSpotifyDataset.csv"
OUTPUT_PATH = "data/songs.csv"

OUTPUT_FIELDS = [
    "id", "title", "artist", "genre", "mood",
    "energy", "tempo_bpm", "valence", "isInstrumental", "duration",
]

# Normalize a handful of Kaggle's track_genre spellings so they line up with
# this project's existing style (see KNOWN_GENRES in recommender.py) instead
# of creating near-duplicate genre tags.
GENRE_ALIASES = {
    "indie-pop": "indie pop",
    "world-music": "world",
    "r-n-b": "r&b",
    "pop-film": "pop",
}

INSTRUMENTAL_THRESHOLD = 0.5

# (valence_bucket, energy_bucket) -> mood, using tertile cutoffs at 1/3, 2/3.
# Distinct from KNOWN_MOODS' original 7 values, this grid adds
# "moody" and "melancholic"/"peaceful"/"chill" splits that reflect actual
# valence/energy combinations rather than one-off manual labels.
MOOD_GRID = {
    ("high", "high"): "happy",
    ("high", "mid"): "happy",
    ("high", "low"): "peaceful",
    ("mid", "high"): "energetic",
    ("mid", "mid"): "chill",
    ("mid", "low"): "relaxed",
    ("low", "high"): "intense",
    ("low", "mid"): "moody",
    ("low", "low"): "melancholic",
}


def _bucket(value: float) -> str:
    if value >= 2 / 3:
        return "high"
    if value >= 1 / 3:
        return "mid"
    return "low"


def derive_mood(valence: float, energy: float) -> str:
    return MOOD_GRID[(_bucket(valence), _bucket(energy))]


def normalize_genre(raw_genre: str) -> str:
    genre = raw_genre.strip().lower()
    return GENRE_ALIASES.get(genre, genre)


def transform(input_path: str = INPUT_PATH, output_path: str = OUTPUT_PATH) -> None:
    seen_track_ids = set()
    by_title_artist = {}  # (title.lower(), artist.lower()) -> (popularity, row_dict)
    dropped_rereleases = 0

    with open(input_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            track_id = row.get("track_id")
            title = row.get("track_name", "").strip()
            artists = row.get("artists", "").strip()
            if not track_id or not title or not artists:
                continue
            if track_id in seen_track_ids:
                continue
            seen_track_ids.add(track_id)

            energy = float(row["energy"])
            valence = float(row["valence"])
            tempo_bpm = round(float(row["tempo"]))
            duration = round(int(row["duration_ms"]) / 1000)
            is_instrumental = float(row["instrumentalness"]) > INSTRUMENTAL_THRESHOLD
            genre = normalize_genre(row["track_genre"])
            mood = derive_mood(valence, energy)
            artist = artists.split(";")[0].strip()
            popularity = float(row["popularity"])

            dedup_key = (title.lower(), artist.lower())
            existing = by_title_artist.get(dedup_key)
            if existing is not None:
                dropped_rereleases += 1
                if popularity <= existing[0]:
                    continue

            by_title_artist[dedup_key] = (popularity, {
                "title": title,
                "artist": artist,
                "genre": genre,
                "mood": mood,
                "energy": energy,
                "tempo_bpm": tempo_bpm,
                "valence": valence,
                "isInstrumental": is_instrumental,
                "duration": duration,
            })

    genres_seen = set()
    moods_seen = set()
    tempo_min = tempo_max = None
    duration_min = duration_max = None
    rows_out = []

    for _, song in by_title_artist.values():
        genres_seen.add(song["genre"])
        moods_seen.add(song["mood"])
        tempo_min = song["tempo_bpm"] if tempo_min is None else min(tempo_min, song["tempo_bpm"])
        tempo_max = song["tempo_bpm"] if tempo_max is None else max(tempo_max, song["tempo_bpm"])
        duration_min = song["duration"] if duration_min is None else min(duration_min, song["duration"])
        duration_max = song["duration"] if duration_max is None else max(duration_max, song["duration"])
        song["id"] = len(rows_out) + 1
        rows_out.append(song)

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows_out)

    print(f"Wrote {len(rows_out)} songs to {output_path}")
    print(f"Dropped {dropped_rereleases} re-release/compilation duplicates (kept highest-popularity version)")
    print(f"tempo_bpm range: {tempo_min}-{tempo_max} (span {tempo_max - tempo_min})")
    print(f"duration range: {duration_min}-{duration_max} (span {duration_max - duration_min})")
    print(f"{len(genres_seen)} distinct genres, {len(moods_seen)} distinct moods")
    print("Genres:", sorted(genres_seen))
    print("Moods:", sorted(moods_seen))


if __name__ == "__main__":
    transform()
