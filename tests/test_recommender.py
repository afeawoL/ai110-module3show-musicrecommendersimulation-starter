import pytest

from src.recommender import Song, UserProfile, Recommender, score_song

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- Edge cases found in Experiment 4 (see README) ---

LOFI_SONG = {
    "genre": "lofi", "mood": "chill", "energy": 0.4,
    "acousticness": 0.8, "instrumentalness": 0.9,
}
INDIE_POP_SONG = {
    "genre": "indie pop", "mood": "happy", "energy": 0.8,
    "acousticness": 0.3, "instrumentalness": 0.1,
}


def genre_points(reasons):
    return [r for r in reasons if "genre" in r]


@pytest.mark.parametrize("genre", ["lofi", "Lofi ", "LOFI", "lo-fi"])
def test_genre_ignores_case_whitespace_and_hyphens(genre):
    _, reasons = score_song({"genre": genre, "mood": "chill", "energy": 0.4}, LOFI_SONG)
    assert genre_points(reasons) == ["genre match: lofi (+2.00)"]


def test_partial_genre_match_needs_whole_words():
    _, related = score_song({"genre": "pop", "mood": "happy", "energy": 0.8}, INDIE_POP_SONG)
    _, letter = score_song({"genre": "o", "mood": "chill", "energy": 0.4}, LOFI_SONG)
    assert genre_points(related) == ["related genre: indie pop ~ pop (+1.00)"]
    assert genre_points(letter) == []


def test_energy_given_as_text_is_converted():
    as_text, _ = score_song({"genre": "lofi", "mood": "chill", "energy": "0.4"}, LOFI_SONG)
    as_number, _ = score_song({"genre": "lofi", "mood": "chill", "energy": 0.4}, LOFI_SONG)
    assert as_text == as_number


@pytest.mark.parametrize("prefs, message", [
    ({"genre": "", "mood": "happy", "energy": 0.8}, "genre must be a non-empty label"),
    ({"genre": "pop", "energy": 0.8}, "missing required keys: mood"),
    ({"genre": "pop", "mood": "happy", "energy": 1.5}, "between 0 and 1"),
    ({"genre": "pop", "mood": "happy", "energy": "loud"}, "energy must be a number"),
])
def test_invalid_profiles_raise_clear_errors(prefs, message):
    with pytest.raises(ValueError, match=message):
        score_song(prefs, LOFI_SONG)
