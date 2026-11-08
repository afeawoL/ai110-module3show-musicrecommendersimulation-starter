# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

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

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
