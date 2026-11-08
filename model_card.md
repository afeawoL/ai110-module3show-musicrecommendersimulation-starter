# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name

**VibeMatch 1.0**: a small music recommender that matches songs to your vibe.

---

## 2. Intended Use

### Goal / task

VibeMatch suggests songs a listener will probably like. You tell it your taste: a favorite genre, a mood, and how energetic you want the music to be. You can also say whether you like acoustic sound and whether you want music without vocals. It then scores every song in its catalog and shows the top 5, with a short reason for each pick.

It doesn't predict exactly what you'll play next. It only finds songs whose features are closest to what you asked for.

### Intended use

- Classroom exploration of how recommender systems work.
- Seeing how changing weights or preferences changes the results.
- Showing that recommendations can be explained ("genre match +2.00, energy close +2.38").

It assumes the user can describe their taste in a few words, and that one taste profile fits them right now.

### Not intended for

- **Real users or a real music app.** The catalog is only 20 made-up songs.
- **Judging music or artists.** A low score means "not a match for this profile," not "a bad song."
- **Learning from behavior.** It never sees what you play or skip, so it can't learn or improve over time.
- **Any decision that matters.** It's a simulation for learning, not a product.

---

## 3. How the Model Works

Think of it as a points game. Every song starts at zero and earns points for each way it matches you:

- **Genre:** +2 points if the song's genre is exactly yours (pop = pop). +1 if it's related (pop and indie pop).
- **Mood:** +1 point if the mood matches exactly. +0.5 if it's a similar mood, like "chill" and "focused." Similar moods are grouped into calm, upbeat, intense, and melancholy.
- **Energy:** up to +2.5 points. The closer the song's energy is to what you want, the more points it gets. Too loud *or* too quiet both lose points.
- **Acoustic sound** (optional): up to +0.5 if the song matches your acoustic or non-acoustic preference.
- **No vocals** (optional): up to +0.75 if the song matches your preference for instrumental music.

The best possible score is 6.75. The system adds up the points for every song, sorts them from highest to lowest, and shows the top 5. Each pick lists the points it earned, so you can see *why* it was chosen.

**Changes from the starter logic:**

- Added the acoustic and no-vocals preferences.
- Added "similar mood" partial credit.
- Raised the energy weight from 1.5 to 2.5, so a song with very wrong energy can't win just by matching the genre.
- Made genre matching ignore capital letters, spaces, and hyphens ("Lo-Fi" = "lofi").
- Added clear error messages for broken profiles, such as a missing mood or energy above 1.

---

## 4. Data

- **Size:** 20 songs. The starter had 10, and I added 10 more.
- **Variety:** 17 genres and 16 moods. Most genres have only **one** song. Lofi has 3 and pop has 2.
- **Features for each song:** genre, mood, energy, tempo, valence (how happy it sounds), danceability, acousticness, instrumentalness (no vocals), and popularity. Energy and the other numbers use a 0–1 scale, except tempo (beats per minute) and popularity (0–100).
- **What I added:** sad and angry songs, because the starter had none. I also added songs that break the usual pattern, like a loud acoustic banjo song and a quiet electronic song. And I added the instrumentalness and popularity columns.
- **Features not used in scoring:** tempo and danceability, because they mostly repeat what energy already says. Valence and popularity are loaded but saved for future experiments.

**Limits:**

- The songs, artists, and numbers are made up by hand, not measured from real music.
- The catalog leans toward Western genres. It has no lyrics, language, or culture information.
- There are gaps: no song is calmer than 0.22 energy, and none are between 0.58 and 0.75.

---

## 5. Strengths

- **Clear, opposite tastes work well.** The High-Energy Pop and Chill Lofi listeners got completely different lists, and both made sense.
- **It explains itself.** Every pick shows the points behind it, so it's easy to spot when something odd happens.
- **Profiles with more detail get better results.** The Late-Night Study listener (acoustic + no vocals) got five calm, instrumental songs with nothing out of place.
- **Energy works like a safety net.** Thanks to the 2.5 weight, a listener asking for calm music no longer gets the loudest pop songs just because the genre matches.
- **It handles messy input.** Typing "Lofi " or "lo-fi" still finds lofi songs. Broken profiles get a clear message instead of a crash.

---

## 6. Limitations and Bias 

The way the system measures the "energy gap" quietly favors songs in the middle of the energy range. Because a song loses points based on its distance from the listener's target energy, a mid-energy song like *Velvet Hours* (energy 0.48) is never far from anyone, while a high-energy song like *Iron Furnace* (energy 0.97) is far from everyone except fans of loud music. When I ran 816 different user profiles (every genre and mood at low, medium, and high energy), *Velvet Hours* appeared in the top 5 about four times as often as *Iron Furnace* (324 times vs. 83), even though nothing about the songs themselves made one better. The formula also treats listeners unequally: no song in the catalog is below 0.22 energy, so a listener who wants very calm music can never get a close match, and there are no songs at all between 0.58 and 0.75, so listeners who want medium-high energy get weaker matches than everyone else. In a real app, this kind of bias would mean extreme or niche music gets recommended less often, which limits what listeners discover.

---

## 7. Evaluation  

### Profiles I tested

I tested four "normal" listeners, each with a different taste:

| Profile | What they asked for | Their top 5 |
| --- | --- | --- |
| **High-Energy Pop** | pop, happy, very energetic (0.90), not acoustic | Sunrise City, Gym Hero, Rooftop Lights, Neon Euphoria, Storm Runner |
| **Chill Lofi** | lofi, chill, calm (0.35), acoustic | Library Rain, Midnight Coding, Focus Flow, Spacewalk Thoughts, Coffee Shop Stories |
| **Deep Intense Rock** | rock, intense, very energetic (0.92), not acoustic | Storm Runner, Gym Hero, Iron Furnace, Crown Heights, Banjo Breakdown |
| **Late-Night Study** | lofi, focused, calm (0.40), acoustic, no vocals | Focus Flow, Library Rain, Midnight Coding, Coffee Shop Stories, Spacewalk Thoughts |

I also tested ten "trick" profiles designed to break the system, such as a listener who wants *sad* music at *high* energy, a genre that doesn't exist ("polka"), a misspelled genre ("lo-fi"), and broken input like a missing mood. For each profile I checked whether the top songs matched what that person asked for, and whether the "Why" reasons made sense.

### Comparing the profiles, pair by pair

**High-Energy Pop vs. Chill Lofi:** These two lists share no songs at all, which is exactly right: they are opposites. Every pop pick is loud and electronic (energy 0.76 or higher), and every lofi pick is quiet and acoustic (energy 0.42 or lower). This shows the energy and acoustic preferences are doing their job of pulling the two listeners to opposite ends of the catalog.

**High-Energy Pop vs. Deep Intense Rock:** These overlap on two songs, *Gym Hero* and *Storm Runner*, because both listeners want loud, non-acoustic music. The difference is mood: the pop fan wants "happy," so the happy song *Sunrise City* wins, while the rock fan wants "intense," so the rock song *Storm Runner* wins and *Sunrise City* doesn't appear. Same energy, different mood, different #1, which makes sense.

**High-Energy Pop vs. Late-Night Study:** No overlap, as expected for a party listener and a study listener. One interesting difference: the study listener's top song scores higher (6.56) than the pop fan's (5.71). That's because the study listener gave more preferences (acoustic *and* no vocals), and the catalog happens to have a song that matches all of them, so there were more chances to earn points.

**Chill Lofi vs. Deep Intense Rock:** No overlap, which is right. But one result surprised me: *Banjo Breakdown*, an acoustic bluegrass song, shows up at #5 for the rock fan even though they said they *don't* like acoustic music. It sneaks in because it's very energetic (0.88) and its mood, "energetic," counts as similar to "intense." The "not acoustic" preference only costs it a small amount, not enough to push it out.

**Chill Lofi vs. Late-Night Study:** These two get the exact same five songs, just in a different order. The only real difference is mood: "focused" instead of "chill." So *Focus Flow*, the one song labeled "focused," jumps from #3 to #1. The study listener's "no vocals" request didn't change anything, because these calm lofi songs already have no vocals. This makes sense: two calm listeners should get similar music, and the small mood change only reorders it.

**Deep Intense Rock vs. Late-Night Study:** No overlap. What stands out is how *spread out* the rock list is: it covers five different genres (rock, pop, metal, hip hop, bluegrass), while the study list has three lofi songs at the top. That's not the algorithm being clever. It's because the catalog has only **one** rock song but three lofi songs, so after *Storm Runner*, the rock fan gets songs that are merely loud.

### Why does "Gym Hero" keep showing up for people who want Happy Pop?

*Gym Hero* is a pop song, but its mood is "intense," not "happy." It still comes in #2 for the High-Energy Pop listener, ahead of *Rooftop Lights*, which actually *is* happy. Here's why, in plain terms: the system gives 2 points for the exact genre "pop" but only 1 point for a mood match. *Gym Hero* gets the full 2 points for being "pop," and its energy (0.93) is almost exactly what the listener asked for (0.90). *Rooftop Lights* is labeled "indie pop," which only counts as half a genre match (1 point); its happy mood adds 1 more, but its energy (0.76) is further off. So being labeled "pop" is worth as much as being both "related to pop" *and* happy. Even for a happy-pop listener who wants medium energy, *Gym Hero* still makes the top 3, because there are only two songs in the whole catalog labeled exactly "pop." In other words, the system trusts the genre label more than the mood, and the small catalog leaves few alternatives.

### What surprised me

- **The genre label is very powerful.** As with *Gym Hero*, a song with the right genre but the wrong mood often beats a song with the right mood but a "related" genre.
- **Small catalogs create odd lists.** The rock fan had only one rock song to choose from, so most of their list was "loud songs from other genres."
- **Conflicting requests lose to genre and mood.** A listener who wanted *sad* folk at *high* energy got a slow song (energy 0.30), because matching the genre and mood (3 points) outweighed the energy request.
- **Mood matters more than it looks.** When I temporarily removed the mood check (Experiment 5 in the README), the pop fan started getting heavy metal and the chill listener got a sad folk song. Mood is what keeps the "feel" right.
- **Trick inputs exposed real bugs.** An empty genre gave *every* song genre points, and a one-letter genre ("o") counted as "related" to seven genres. I fixed these and added tests.

### Tests and comparisons I ran

- **Unit tests:** 12 automated tests in `tests/test_recommender.py` check sorting, explanations, label clean-up (e.g. "Lo-Fi" = "lofi"), and that broken profiles give clear errors. All pass.
- **Weight experiments:** I compared four weighting strategies and several energy weights (README Experiments 1–3 and 5) and checked how much each changed the top 5.
- **Exposure check:** I ran 816 profiles (every genre and mood at three energy levels) and counted how often each song was recommended. This revealed the mid-energy bias described in *Limitations and Bias*.

---

## 8. Future Work

Ideas for improvement:

1. **Mix up the top 5.** Right now a lofi fan always gets the same three lofi songs, two by the same artist. I'd add a rule that limits one artist per list and saves a spot for something new, to break the filter bubble.
2. **Fix the energy bias.** Mid-energy songs get recommended about 4× as often as very loud ones. I'd fill the gaps in the catalog (very calm songs, and songs between 0.58 and 0.75). I'd also try scoring energy relative to the songs that are actually available.
3. **Understand genres, not just labels.** "Hip hop" and "rap" should count as related, and so should rock and metal. A small "related genres" list, like the mood groups, would help. So would a much bigger catalog, so niche fans don't run out of matches after one song.

---

## 9. Personal Reflection

### Biggest learning moment

My biggest learning moment was the sensitivity test (Experiment 5). I doubled the energy weight, halved the genre weight, and turned off the mood check. Suddenly the happy pop fan was getting heavy metal, and the chill lofi fan got a sad folk song. Before that, I thought of the weights as small tuning numbers. After it, I saw that they *are* the recommender's opinion about what matters. Changing a 2.0 to a 1.0 changes who the system works well for.

### How AI tools helped, and when I had to double-check

AI tools helped me move fast. They summarized how Spotify and YouTube recommend music, analyzed the dataset, wrote first versions of the scoring code, and formatted the terminal output. They were especially useful for running the same test across many profiles at once.

But I had to double-check them several times:

- **Facts from memory:** the first research summary came from the AI's memory. When I asked it to check the web, it found that Spotify had shut off its public audio-features API for new apps in late 2024. That detail matters if you want to use real Spotify data.
- **AI-written code had bugs:** the "related genre" rule looked fine, but when I tested trick profiles, an empty genre gave *every* song genre points, and the letter "o" counted as related to seven genres. Only testing on purpose found that.
- **Numbers had to be re-run:** some experiment results first came from a quick test script, not my real code. I had to re-run them once the code was finished to make sure the README matched.
- **Claims had to match the evidence:** one note said negative energy points showed up in a profile's top 5, but they only appeared further down the list. I had to correct it.

The lesson: AI is a fast helper, but I'm responsible for checking that what it says matches what the code actually does.

### What surprised me about simple algorithms

I was surprised how much a simple points system *feels* like a real recommendation. It's just adding up a few numbers, but when the output says "genre match +2.00, energy close +2.38," it feels thoughtful, almost like a friend explaining a pick. That's also what makes it a little dangerous. *Gym Hero* showed up for happy pop fans because the "pop" label is worth a lot, not because the system understood anything about happiness. And a song like *Velvet Hours* got recommended four times as often as *Iron Furnace*, just because its energy sits in the middle. Simple rules can look smart and still be quietly unfair.

### What I'd try next

- **Collaborative filtering:** make fake listening histories and recommend songs that similar listeners liked. Then compare it to my content-based approach.
- **Variety in the top 5:** limit each list to one song per artist and save a slot for something unexpected, to break the filter bubble.
- **A popularity experiment:** give a bonus to popular songs and measure whether niche songs disappear, like the popularity bias I read about.
- **A bigger catalog:** so fans of genres like rock or metal don't run out of real matches after one song.
