# System Diagram

```mermaid
flowchart TD
    User(["User"])

    subgraph DataLayer["Data Layer"]
        Kaggle[(Kaggle Spotify Dataset)]
        LoadSongs["transform_kaggle_data()"]
        SongDB[(Song Database)]
        Kaggle --> LoadSongs --> SongDB
    end

    subgraph ProfileCreation["User Profile Creation"]
        InputChoice{"Mood Description"}
        MoodText["Free-text mood description"]
        TextToProfile{{"text_to_profile()\n(LLM call)"}}
        UserProfile["User Profile (dict)"]

        InputChoice -->|Describe mood in words| MoodText --> TextToProfile --> UserProfile
    end

    subgraph Recommender["Recommendation Engine"]
        ScoreSong["score_song()\nscore each song vs. profile"]
        RecommendSongs["recommend_songs()\nsort, take top-k"]
        TopK["Top-K songs + scores + reasons"]

         ScoreSong --> RecommendSongs --> TopK
    end

    subgraph ExplanationLayer["Explanation"]
        ExplainLLM{{"generate_explanation()\n(LLM call)"}}
        FriendlyOutput["Friendly explanation\n+ recommended songs"]
        ExplainLLM --> FriendlyOutput
    end

    User --> InputChoice
    SongDB --> ScoreSong
    UserProfile --> ScoreSong
    TopK --> ExplainLLM
    FriendlyOutput --> User
```

Hexagon nodes (`text_to_profile()`, `generate_explanation`) marks where
an LLM call replaces deterministic functional code — everything else in the
pipeline is a pure function operating on plain dicts/lists.
