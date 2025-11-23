# Nirmaan AI Intern Case Study: Student Introduction Scorer

## Project Overview
This project is an AI-powered tool built using **Streamlit** that analyzes spoken self-introduction transcripts and generates a holistic score (0-100) and detailed, per-criterion feedback based on a defined rubric. 

It fulfills the case study requirement of combining **rule-based checks**, **NLP-based semantic scoring**, and **data-driven weighting** to evaluate student communication skills.

## Features
* **Transcript Scoring**: Accepts pasted text or a transcript file as input via a Streamlit UI.
* **Multi-Faceted Rubric**: Scores transcripts on criteria like Salutation, Content & Structure, Speech Rate, Language & Grammar, Clarity (Filler Words), and Engagement.
* **Detailed Feedback**: Provides an overall score, per-criterion scores, and specific textual feedback.
* **NLP & Rule-Based Logic**: Combines semantic similarity checks (using Sentence Transformers) with keyword matching and statistical analysis (like WPM and grammar checks).
* **JSON Output**: Allows viewing and downloading the full scoring output in JSON format.

## 🧠 Scoring Formula Description

The overall score is a normalized value (0-100) calculated from the weighted sum of individual criterion scores.

### 1. Per-Criterion Scoring (0 to Max Weight)
Each criterion is scored based on the defined weight and uses one or more of the required approaches:

| Criterion | Submission Weight | Primary Approach | Key Logic Used |
| :--- | :--- | :--- | :--- |
| **Salutation** | 5 | Rule-Based | Checks for the presence of specific greeting keywords (e.g., 'hello', 'good morning') in the first sentence. |
| **Content & Structure** | 20 | NLP-Based & Rule-Based | Calculates **Cosine Similarity** between the transcript and the target content description using a pre-trained **Sentence Transformer** model (`all-MiniLM-L6-v2`). Also uses rule-based checks for necessary keywords (name, school, family, etc.). |
| **Speech Rate** | 15 | Rule-Based / Statistical | Calculates the **Words Per Minute (WPM)** and scores based on the WPM falling within a target range (e.g., 100-150 WPM). |
| **Language & Grammar** | 30 | Rule-Based / External Tool | Uses the `language-tool-python` library to find and count grammar/spelling mistakes. Score is penalized based on the error density (errors per 100 words). |
| **Clarity** | 20 | Rule-Based | Counts the frequency of filler words (e.g., 'um', 'uh', 'you know'). Score is penalized for higher filler word density. |
| **Engagement** | 10 | Rule-Based / Lexicon | Counts the presence of a list of positive/enthusiastic words and checks for emotional expression keywords. |

### 2. Final Score Calculation (Data/Rubric-Driven Weighting)
1.  **Weighted Sum**: The individual score for each criterion is multiplied by its defined weight in the rubric.
    $$
    Score_{Total} = \sum (\text{Criterion Score} \times \text{Criterion Weight})
    $$
2.  **Normalization**: The total score is normalized to a 0-100 range by dividing the weighted sum by the maximum possible total weighted score ($\sum \text{Weights} = 100$).
    $$
    Final Score = \frac{Score_{Total}}{\text{Max Possible Score}} \times 100
    $$

## 🛠️ Run Instructions (Quick Start)
For detailed setup and deployment instructions, please refer to **`DEPLOYMENT.md`**.

1.  Clone the repository.
2.  Install dependencies: `pip install -r requirements.txt`
3.  Run the Streamlit application: `streamlit run app.py`
4.  The application will open in your web browser (usually at `http://localhost:8501`).