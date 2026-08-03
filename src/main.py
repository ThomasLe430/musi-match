"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, score_song, recommend_songs


def main() -> None:
    # Returns a list of dictionaries representing each song
    songs = load_songs("data/songs.csv") 
    
    # Starter example profile (updated from original)
    happy_pop_user = {"artist":"Taylor Swift",
                   "genre": "pop",
                   "mood": "happy",
                   "energy": 0.8,
                   "valence":0.8,
                   "instrumental": False,
                    "tempo_bpm": None,
                    "duration": 150 }
    chill_lofi_user = { "artist": "LoRoom",
                       "genre": ["lofi", "orchestral", "ambient"],
                       "mood": ["chill", "peaceful"],
                       "energy": 0.4,
                       "valence": 0.6,
                       "instrumental": True,
                       "tempo_bpm": 80,
                       "duration": 180 }
    asian_music_enjoyer = { "artist": "BTS",
                            "genre": ["k-pop", "j-rock"],
                            "mood": ["happy", "energetic"],
                            "energy":0.85,
                            "valence": 0.75,
                            "instrumental": None,
                            "tempo_bpm": 120,
                            "duration": 125 }
    
    intense_rock_user = {"artist": "Voltline",
                        "genre": ["rock", "j-rock"],
                        "mood": ["intense", "moody"],
                        "energy":0.9,
                        "valence":0.3,
                        "instrumental": False,
                        "tempo_bpm": 150,
                        "duration": 180}
    omnivore_user = {"artist": None,
                  "genre": ["pop", "rock", "lofi", "jazz", "ambient", "electronic",
                            "classical", "k-pop", "j-rock", "synthwave", "indie pop", "world"],
                  "mood": None,
                  "energy": 0.9,
                  "valence": 0.9,
                  "instrumental": None,
                  "tempo_bpm": None,
                  "duration": None}
    
    user_list = [happy_pop_user, chill_lofi_user, asian_music_enjoyer, intense_rock_user, omnivore_user]
    
    for user in user_list:
        recommendations = recommend_songs(user, songs, k=5)

        print("\nTop recommendations:\n")
        for rank, (song, score, explanation) in enumerate(recommendations, start=1):
            print(f"{rank}. {song['title']} — {song['artist']} ({score:.0%} Match)")
            print(" Reasoning:", f" {explanation}")
            print()


if __name__ == "__main__":
    main()
