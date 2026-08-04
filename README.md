# 🎧 MusiMatch 🎧
Created by Thomas Le.

## Original Project
MusiMatch is an extension of CodePath AI110's Music Recommender Simulation. The goal of the original project is to gain familiarity with content-based retrieval and how data like songs can be quantified into feature vectors. 

##  Summary

This new project, MusiMatch extends the recommender by using an end-to-end AI system that streamlines the process of describing your mood and generating an understanable explanation. Rather than manually inputting a profile, the user can describe their mood in natural language, which is fed into the recommender system and outputs the recommendation seamlessly. Combined with a large database of songs (~80K), MusiMatch delivers quality results with text-based recommendation that music streaming services often do not provide. 

---

## Architecture Overview

First, the user is prompted to enter a textual description of the musical mood they desire (stating preferences in artist, genre, mood, energy etc). The AI (Gemini Flash 3.5 Lite) converts the text into a dictionary that is compatible with the recommendation algorithm. Then, the dictionary represented the user profile is used to search the song database for the top-k songs with the highest score. The recommended songs and scores are then fed back into the AI to generate a friendly explanation of why the recommended songs are chosen.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

 ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows
```

2. Install dependencies

```bash
  pip install -r requirements.txt
```

3. Run the app:

```bash
  python -m src/main.py
```

### Running Tests

Run the starter tests with:

```bash
python -m pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

```
Describe the kind of song you're in the mood for: I want some intense rock music to fuel my workout sessions at the gym. I need the songs to be fast, energizing, and adrenaline-inducing. 

Top recommendations:

1. Go Your Own Way - 2018 Remaster — Fleetwood Mac (99% Match)
 Reasoning:  This high-energy rock classic is a near-perfect match for your tastes, perfectly capturing the intense, upbeat mood you're looking for with a 99% compatibility score.

2. Danger Zone - From "Top Gun" Original Soundtrack — Kenny Loggins (99% Match)
 Reasoning:  With a high-energy rock sound and an intense, upbeat vibe, "Danger Zone" by Kenny Loggins is a near-perfect match for your energetic preferences. It hits all the right notes for your taste with a stellar 99% compatibility score!

3. Shut Off The Lights — Bastille (99% Match)
 Reasoning:  "Shut Off The Lights" by Bastille is a near-perfect match for your taste, delivering the high-energy rock vibe and upbeat mood you're looking for.

4. Superheroes — The Script (99% Match)
 Reasoning:  With an energetic rock sound and a high energy score of 0.885, "Superheroes" by The Script is a near-perfect match for your taste in intense, high-tempo music.

5. Don't Stop Me Now - Remastered 2011 — Queen (98% Match)
 Reasoning:  With a sky-high score of 98.4%, "Don't Stop Me Now" by Queen is a near-perfect match for your rock playlist. Its blistering energy and upbeat tempo hit every single mark for the intense, high-energy vibe you're looking for.

---------------------------------------------------------------------
 Describe the kind of song you're in the mood for: I've heard alot about the K-pop group BTS and I want to hear some of their songs. I am looking for ones that are energetic and poppy! 

Top recommendations:

1. Boy With Luv (feat. Halsey) — BTS (100% Match)
 Reasoning:  With a near-perfect match to your favorite artists, upbeat mood, and high energy level, "Boy With Luv (feat. Halsey)" hits every mark on your K-pop and pop wishlist. It's an ideal fit for your upbeat taste, scoring a phenomenal 99.7% compatibility!

2. Look Here — BTS (100% Match)
 Reasoning:  This track is a near-perfect match for your taste, combining your love for BTS with a high-energy, happy vibe that aligns seamlessly with your preferred tempo and mood.

3. Love Maze — BTS (99% Match)
 Reasoning:  Based on your love for BTS and upbeat, happy K-pop, "Love Maze" is a near-perfect match with its high energy and joyful vibe.

4. Anpanman — BTS (99% Match)
 Reasoning:  Because you love BTS and are looking for high-energy, happy K-pop, "Anpanman" is a stellar match with its upbeat tempo and joyful vibe. It hits almost every single one of your musical preferences with a near-perfect score!

5. Airplane pt.2 — BTS (99% Match)
 Reasoning:  With an exceptional 99% match, BTS's "Airplane pt.2" hits all the right notes for your taste with its upbeat K-pop sound, high energy, and undeniably happy vibe.
---------------------------------------------------------------------
Describe the kind of song you're in the mood for: I need some chill and peaceful songs that I can do some homework to. I have no preference for artists, but the song should be on the slower side, short, and have no instrumental. 

1. Too Tired — Smartface (99% Match)
 Reasoning:  With its ultra-low energy and relaxed mood, "Too Tired" by Smartface is a nearly perfect match for your chill study session.

2. Wax Poetry — Dazik69 (99% Match)
 Reasoning:  With a perfect blend of relaxed energy and a peaceful study vibe, "Wax Poetry" by Dazik69 is an ideal match for your focus sessions. Its gentle mood and calm tempo align seamlessly with your preferred listening style.

3. $tars and I feel alone — Vluestar (99% Match)
 Reasoning:  "$tars and I feel alone" by Vluestar is a near-perfect match for your tastes, perfectly capturing your preferred chill mood and low-energy vibe. Its relaxed atmosphere and balanced valence align seamlessly with your ideal study and relaxation soundtrack.

4. Home By 11 PM — Sarah, the Illstrumentalist (99% Match)
 Reasoning:  "Home By 11 PM" by Sarah, the Illstrumentalist is an almost-perfect match for your tastes, perfectly aligning with your preferred study genre and relaxed mood. Its gentle energy and positive valence hit your ideal targets for a calm, focused listening session.

5. More & More — Finding Hope (99% Match)
 Reasoning:  "More & More" by Finding Hope is an almost perfect match (98.9% score) because its relaxed mood, gentle chill genre, and soft energy level closely align with your peaceful study preferences.

```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Design Decisions
My design philosophy emphasized speed and ease of use. A more complex music recommendation algorithm might consider popularity or context-based information, but I decided to focus on content-based because I wanted the model to prioritize what the user is feeling in that moment. I went with a functional-based design (rather than object oriented) because of the emphasis on the mathematical recommendation algorithm and how data doesn't really need to be altered throughout the pipeline. One of the trade-offs is that scalability is more difficult. If I ever wanted to add more dimensions to songs or information on a user profile, a lot of the system would have to be changed.

---

## Testing Summary
The testing primarily focuses on verifying the recommendation algorithm produces sane results and those results are consist across similar user profiles. Test_recommender.py tests basic recommender functionality; test_reliability.py ensures that reliability scoring is stable and integrated with system functionality. The in-depth results of the reliability test can be found in reliability_report.json, where I tested that three similar text inputs describing the same mood results in similar generated user profiles (describing chill, lofi songs). Using measures of similarity to see if the generated user profiles were similar, we found the model to have a reliability score of 92.5%.

---

## Reflection
This project taught me that AI-assisted development is a powerful tool that allows me to bring my vision to life without the hassle of technical implementation. In other words, I learned that I need to focus on clarity, design choices, and reliability when working with AI. I never let the AI take over the vision for me - I always made sure I understood what it was outputting and pushed back when it did too much. 


