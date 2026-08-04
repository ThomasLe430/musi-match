# 🎧 Model Card: Music Recommender

## 1. Model Name  

**MusiMatch**
---

## 2. Intended Use  
The model is meant to take in natural language explanation of the user's musical mood and output a list of recommended songs + explanations. The model is intended for classroom and personal use.

---

## 3. How the Model Works  

First, the user is prompted to enter a textual description of the musical mood they desire (stating preferences in artist, genre, mood, energy etc). The AI (Gemini Flash 3.5 Lite) converts the text into a dictionary that is compatible with the recommendation algorithm. Then, the dictionary represented the user profile is used to search the song database for the top-k songs with the highest score. The recommended songs and scores are then fed back into the AI to generate a friendly explanation of why the recommended songs are chosen.

---

## 4. Data  
The data is sourced from https://www.kaggle.com/datasets/maharshipandya/-spotify-tracks-dataset/data. The data was cleaned and transformed into songs.csv. 

---

## 5. Strengths  

The model exceeds at finding strong artist, genre, and mood matches. If the user provides enough details, the model recommends with confidence. Furthermore, the model is simply to use and the explanations it generates are easy to understand.  

---

## 6. Limitations and Bias 
The model prioritzes genre, meaning that the songs that the system recommends could be limited in scope. For example, the user could indicate that they want a rock song, but the system might ignore j-rock, alt rock, or punk rock - genres that are adjacent but ignored because they wall into a different category. The model also has no built in randomness, so recommendations might be repetitive to the user. 

---

## 7. Reliability and Evaluation  
In short, I tested if similar inputs consistently led to similar outputs in the profile creation phase. If the user describes the same musical profile, but with slightly different wording, the generated profiles should be similar. To test this (in reliability.py), I created functions to measure similarity and streamlined the process of generating profiles repeatedly.The similarity scores are the main metric for evaluation -- higher similarity means same profiles are leading the the same recommendations, a consistency that is crucial in an AI system like this. The resulting score of 92.5% in reliability_report.json demonstrates how the system is reliable given ethis framework. 

---

## 8. AI Collaboration  
Collaboration with AI (Claude for coding, Gemini for text parsing) focused on mutual understanding and preserving my vision for the project. One example where the AI gave a helpful suggestion was when I was developing a function to call an API to generate a user profile from text input. To be honest, I had no idea where to start because it was my first time making an API call to an external model and I wasn't sure which model to even use. Claude presented me with options to use and helped with the prompting process. 
One example where AI gave a flawed suggestion was when I was designing the reliability system. When I first came up with the plan, the AI wanted to go overboard - guardrails, evaluation, and reliability all in one go. I had to push back and say that I wanted to focus on reliability first before implementing guardrails to take development one step at a time. Overall, the AI tends to be over-ambitious and I had many occasions where I had to push back and double check my understanding.

---

## 9. Final Reflection  
Ultimately, developing this model has showed me that AI is a powerful tool that can allow me to focus on overall system design + reliability, rather than tricky implementation. Although I do enjoy implementing things myself, I am confident that without AI this project would've taken me significantly longer. Some careful navigation was required to ensure that the AI didn't over extend and kept my vision intact. 