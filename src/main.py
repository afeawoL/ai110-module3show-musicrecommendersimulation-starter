"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import argparse
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
# Warn when even the best song scores under half of what was possible
WEAK_MATCH_RATIO = 0.5
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

# Standard listener profiles, run by default
PROFILES = {
    "high-energy-pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.90,
        "likes_acoustic": False,
    },
    "chill-lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "likes_acoustic": True,
    },
    "deep-intense-rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "likes_acoustic": False,
    },
    "late-night-study": STUDY_LISTENER,
}

# Adversarial profiles that probe weak spots in the scoring (run with --edge-cases)
EDGE_CASE_PROFILES = {
    # Conflict: sad songs in the catalog are all low energy
    "sad-but-energetic": {"genre": "folk", "mood": "sad", "energy": 0.90},
    # Conflict: the only classical song is very acoustic
    "instrumental-not-acoustic": {
        "genre": "classical",
        "mood": "melancholy",
        "energy": 0.20,
        "likes_acoustic": False,
        "wants_instrumental": True,
    },
    # Nothing matches: ranking falls back to energy alone (flagged as a weak match)
    "unknown-genre-and-mood": {"genre": "polka", "mood": "silly", "energy": 0.50},
    # Substring trick: "" used to be "inside" every genre (now rejected as empty)
    "empty-genre": {"genre": "", "mood": "happy", "energy": 0.80},
    # Substring trick: "o" used to match lofi, pop, rock... (now whole words only)
    "one-letter-genre": {"genre": "o", "mood": "chill", "energy": 0.50},
    # Formatting: capital letter and trailing space (now ignored)
    "messy-genre-text": {"genre": "Lofi ", "mood": "chill", "energy": 0.35},
    # Spelling: "lo-fi" vs. "lofi" (hyphens now ignored)
    "alternate-spelling": {"genre": "lo-fi", "mood": "chill", "energy": 0.35},
    # Out of range: energy outside 0-1 (now rejected)
    "energy-out-of-range": {"genre": "metal", "mood": "angry", "energy": 1.50},
    # Wrong type: energy given as text (now converted to a number)
    "energy-as-text": {"genre": "pop", "mood": "happy", "energy": "0.8"},
    # Missing key: no mood (now a clear error instead of a crash)
    "missing-mood": {"genre": "pop", "energy": 0.80},
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
    filled = min(max(round(BAR_WIDTH * score / best), 0), BAR_WIDTH)
    return "█" * filled + "░" * (BAR_WIDTH - filled)


def print_profile(name: str, user_prefs: dict) -> None:
    print("=" * WIDTH)
    print("🎵  MUSIC RECOMMENDER".center(WIDTH))
    print("=" * WIDTH)
    print(f"Profile: {name}")
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


def run_profile(name: str, user_prefs: dict, songs: list, k: int) -> None:
    """Prints one profile and its top k recommendations, or the error it caused."""
    print_profile(name, user_prefs)
    try:
        recommendations = recommend_songs(user_prefs, songs, k=k)
    except ValueError as error:
        print(f"\n⚠️  Invalid profile: {error}")
        print("=" * WIDTH + "\n")
        return

    best = max_score(user_prefs)
    top_score = recommendations[0][1] if recommendations else 0.0
    if top_score < WEAK_MATCH_RATIO * best:
        print(f"\n⚠️  Weak match: the best song scores {top_score:.2f} of {best:.2f}.")
        print("    Nothing in the catalog fits this profile well; results are closest guesses.")
    print(f"\nTop {len(recommendations)} recommendations:")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print_recommendation(rank, song, score, explanation, best)
    print("=" * WIDTH + "\n")


def parse_args() -> argparse.Namespace:
    all_names = [*PROFILES, *EDGE_CASE_PROFILES]
    parser = argparse.ArgumentParser(description="Run the music recommender simulation.")
    parser.add_argument("--profile", choices=all_names, help="run a single named profile")
    parser.add_argument("--edge-cases", action="store_true", help="run the adversarial profiles")
    parser.add_argument("-k", type=int, default=5, help="number of recommendations (default 5)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    songs = load_songs(SONGS_CSV)
    print(f"Loaded songs: {len(songs)}\n")

    if args.profile:
        profiles = {args.profile: {**PROFILES, **EDGE_CASE_PROFILES}[args.profile]}
    elif args.edge_cases:
        profiles = EDGE_CASE_PROFILES
    else:
        profiles = PROFILES

    for name, user_prefs in profiles.items():
        run_profile(name, user_prefs, songs, args.k)


if __name__ == "__main__":
    main()
