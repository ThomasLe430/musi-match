import argparse

from recommender import load_songs, text_to_profile, recommend_songs
from reliability import run_reliability_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-reliability",
        action="store_true",
        help="Run the text_to_profile consistency report instead of asking for a description.",
    )
    args = parser.parse_args()

    if args.check_reliability:
        run_reliability_report()
        return

    # Returns a list of dictionaries representing each song
    songs = load_songs("data/songs.csv")

    desc = input("Describe the kind of song you're in the mood for: ").strip()
    user_prefs = text_to_profile(desc)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} — {song['artist']} ({score:.0%} Match)")
        print(" Reasoning:", f" {explanation}")
        print()


if __name__ == "__main__":
    main()
