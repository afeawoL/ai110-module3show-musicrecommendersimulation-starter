"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import re
from pathlib import Path

try:
    import src.recommender as rec  # python -m src.main
except ImportError:
    import recommender as rec  # python src/main.py

load_songs, recommend_songs = rec.load_songs, rec.recommend_songs

# Resolve the CSV relative to this file so the app runs from any folder
SONGS_CSV = Path(__file__).resolve().parent.parent / "data" / "songs.csv"

WIDTH = 64
BAR_WIDTH = 20
# Splits "genre match: lofi (+2.00)" into ("genre match: lofi", "+2.00")
REASON_PATTERN = re.compile(r"^(.*) \(([+-][\d.]+)\)$")


# Taste profile: a late-night study listener who wants calm, focused,
# mostly acoustic background music. Keys match what score_song() reads.
STUDY_LISTENER = {
    "genre": "lofi",             # favorite genre: +2.0 exact match, +1.0 partial
    "mood": "focused",           # favorite mood: +1.0 match
    "energy": 0.40,              # target energy (0-1): closer = more points
    "likes_acoustic": True,      # prefers acoustic over produced sound
    "wants_instrumental": True,  # no vocals while studying
}


def max_score(user_prefs: dict) -> float:
    """Best possible score for this profile (optional rules count only if set)."""
    total = rec.GENRE_WEIGHT + rec.MOOD_WEIGHT + rec.ENERGY_WEIGHT
    if user_prefs.get("likes_acoustic") is not None:
        total += rec.ACOUSTIC_WEIGHT
    if user_prefs.get("wants_instrumental") is not None:
        total += rec.INSTRUMENTAL_WEIGHT
    return total


def score_bar(score: float, best: float) -> str:
    """Draws a bar like ███████████████░░░░░ showing score out of best."""
    filled = round(BAR_WIDTH * score / best)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def print_profile(user_prefs: dict) -> None:
    print("=" * WIDTH)
    print("🎵  MUSIC RECOMMENDER".center(WIDTH))
    print("=" * WIDTH)
    print("Your taste profile:")
    for key, value in user_prefs.items():
        print(f"  {key.replace('_', ' '):<20} {value}")


def print_recommendation(rank: int, song: dict, score: float, explanation: str, best: float) -> None:
    print("-" * WIDTH)
    print(f"#{rank}  {song['title']}  ·  {song['artist']}")
    print(f"    {song['genre']} / {song['mood']}")
    print(f"    Score {score:.2f} / {best:.2f}  {score_bar(score, best)}")
    print("    Why:")
    for reason in explanation.split("; "):
        match = REASON_PATTERN.match(reason)
        if match:
            text, points = match.groups()
            print(f"      • {text:<44}{points:>7}")
        else:
            print(f"      • {reason}")


def main() -> None:
    songs = load_songs(SONGS_CSV)
    print(f"Loaded songs: {len(songs)}\n")

    user_prefs = STUDY_LISTENER
    recommendations = recommend_songs(user_prefs, songs, k=5)
    best = max_score(user_prefs)

    print_profile(user_prefs)
    print(f"\nTop {len(recommendations)} recommendations:")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation, best)
    print("=" * WIDTH)


if __name__ == "__main__":
    main()
