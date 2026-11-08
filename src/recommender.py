import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# Algorithm Recipe weights (see README "How The System Works")
GENRE_WEIGHT = 2.0
MOOD_WEIGHT = 1.0
ENERGY_WEIGHT = 2.5  # raised from 1.5 so a large energy mismatch can outweigh genre (Experiment 3)
ACOUSTIC_WEIGHT = 0.5
INSTRUMENTAL_WEIGHT = 0.75

# Moods in the same group earn partial credit (e.g. "chill" for a "focused" user)
MOOD_GROUPS = {
    "calm": {"chill", "relaxed", "focused", "dreamy", "romantic"},
    "upbeat": {"happy", "uplifting", "euphoric"},
    "intense": {"intense", "angry", "energetic", "confident"},
    "melancholy": {"sad", "melancholy", "moody", "nostalgic"},
}

def _mood_group(mood: str) -> Optional[str]:
    """Returns the name of the group a mood belongs to, or None."""
    for group, moods in MOOD_GROUPS.items():
        if mood in moods:
            return group
    return None

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float
    # Defaults keep older code (and tests) that omit these fields working
    instrumentalness: float = 0.0
    popularity: int = 0

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    # None means "no preference", so the instrumental rule is skipped
    wants_instrumental: Optional[bool] = None

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        prefs = _profile_to_prefs(user)
        by_id = {song.id: song for song in self.songs}
        ranked = recommend_songs(prefs, [asdict(song) for song in self.songs], k)
        return [by_id[song["id"]] for song, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        score, reasons = score_song(_profile_to_prefs(user), asdict(song))
        return f"Score {score:.2f}: " + "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    int_fields = {"id", "popularity"}
    float_fields = {
        "energy", "tempo_bpm", "valence", "danceability",
        "acousticness", "instrumentalness",
    }

    songs = []
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            for field in int_fields & row.keys():
                row[field] = int(row[field])
            for field in float_fields & row.keys():
                row[field] = float(row[field])
            songs.append(row)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    def award(points: float, reason: str) -> None:
        """Adds points and records why, e.g. "genre match: lofi (+2.0)"."""
        nonlocal score
        score += points
        reasons.append(f"{reason} (+{points:.2f})")

    # Genre: exact match beats a partial one ("pop" inside "indie pop")
    genre, fav_genre = song["genre"].lower(), user_prefs["genre"].lower()
    if genre == fav_genre:
        award(GENRE_WEIGHT, f"genre match: {song['genre']}")
    elif fav_genre in genre or genre in fav_genre:
        award(GENRE_WEIGHT / 2, f"related genre: {song['genre']} ~ {user_prefs['genre']}")

    # Mood: exact match, or partial credit for a mood in the same group
    mood, fav_mood = song["mood"].lower(), user_prefs["mood"].lower()
    if mood == fav_mood:
        award(MOOD_WEIGHT, f"mood match: {song['mood']}")
    elif _mood_group(mood) is not None and _mood_group(mood) == _mood_group(fav_mood):
        award(MOOD_WEIGHT / 2, f"similar mood: {song['mood']} ~ {user_prefs['mood']}")

    # Energy: reward closeness to the target, not higher or lower values
    energy_gap = abs(song["energy"] - user_prefs["energy"])
    award(
        ENERGY_WEIGHT * (1 - energy_gap),
        f"energy {song['energy']:.2f} vs. your target {user_prefs['energy']:.2f}",
    )

    # Acoustic fit only applies when the user stated a preference
    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        acousticness = song["acousticness"]
        fit = acousticness if likes_acoustic else 1 - acousticness
        label = "acoustic" if likes_acoustic else "produced (non-acoustic)"
        award(ACOUSTIC_WEIGHT * fit, f"{label} sound, acousticness {acousticness:.2f}")

    # Instrumental fit only applies when the user stated a preference
    wants_instrumental = user_prefs.get("wants_instrumental")
    if wants_instrumental is not None:
        instrumentalness = song.get("instrumentalness", 0.0)
        fit = instrumentalness if wants_instrumental else 1 - instrumentalness
        label = "instrumental" if wants_instrumental else "vocals"
        award(INSTRUMENTAL_WEIGHT * fit, f"{label}, instrumentalness {instrumentalness:.2f}")

    return round(score, 2), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    # Generator: pairs each song with its (score, reasons) without building a list yet
    scored = ((song, *score_song(user_prefs, song)) for song in songs)

    # sorted() returns a new list and leaves the caller's `songs` untouched.
    # It's stable, so ties keep catalog order even with reverse=True.
    ranked = sorted(scored, key=lambda item: item[1], reverse=True)[:k]

    return [(song, score, "; ".join(reasons)) for song, score, reasons in ranked]

def _profile_to_prefs(user: UserProfile) -> Dict:
    """Converts a UserProfile into the dict format score_song expects."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": user.target_energy,
        "likes_acoustic": user.likes_acoustic,
        "wants_instrumental": user.wants_instrumental,
    }
