
import os
import re
import string
import sqlite3

import streamlit as st
import pandas as pd
import nltk
import torch

from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.sentiment import SentimentIntensityAnalyzer

from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)

from sentence_transformers import (
    SentenceTransformer,
    util
)


# ============================================================
# 1. PAGE SETUP
# ============================================================

st.set_page_config(
    page_title="MoodMentor Dashboard",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 MoodMentor")
st.caption(
    "AI-Based Employee Wellness Management Platform"
)

st.markdown(
    """
    Analyze emotional states and receive personalized
    wellness recommendations.
    """
)


# ============================================================
# 2. NLTK RESOURCES
# ============================================================

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("vader_lexicon", quiet=True)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words("english"))
sia = SentimentIntensityAnalyzer()


# ============================================================
# 3. FILE PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MODEL_PATH = os.path.abspath(
    os.path.join(BASE_DIR, "..", "milestone 2", "distilbert_multilabel_emotion_model")
)

MILESTONE3_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "milestone3")
)

HYBRID_FILE = os.path.join(MILESTONE3_DIR, "hybrid_recommendation_dataset.csv")
WELLNESS_FILE = os.path.join(MILESTONE3_DIR, "wellness_content_dataset.csv")
DATABASE_FILE = os.path.join(MILESTONE3_DIR, "moodmentor.db")


# ============================================================
# 4. EMOTION LABELS
# ============================================================

EMOTION_LABELS = [
    "joy",
    "sadness",
    "anger",
    "fear",
    "surprise",
    "disgust"
]


# ============================================================
# 5. LOAD EMOTION MODEL
# ============================================================

@st.cache_resource
def load_emotion_model():

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_PATH
    )

    model.eval()

    return tokenizer, model


# ============================================================
# 6. LOAD SEMANTIC MODEL
# ============================================================

@st.cache_resource
def load_semantic_model():

    return SentenceTransformer(
        "all-MiniLM-L6-v2"
    )


tokenizer, emotion_model = load_emotion_model()
semantic_model = load_semantic_model()


# ============================================================
# 7. DATABASE INITIALIZATION
# ============================================================

def initialize_database():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS emotional_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            text TEXT,
            emotion TEXT,
            confidence REAL,
            intensity TEXT,
            sentiment TEXT
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            recommendation TEXT,
            accepted TEXT,
            rating INTEGER
        )
        """
    )

    connection.commit()
    connection.close()


initialize_database()


# ============================================================
# 8. TEXT VALIDATION
# ============================================================

def validate_text(text):

    return bool(
        text and text.strip()
    )


# ============================================================
# 9. TEXT PREPROCESSING
# ============================================================

def preprocess(text):

    if not validate_text(text):

        return {
            "error": "Empty text provided."
        }

    cleaned = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    no_special = re.sub(
        r"[^a-zA-Z0-9\s]",
        "",
        cleaned
    )

    no_punct = no_special.translate(
        str.maketrans(
            "",
            "",
            string.punctuation
        )
    )

    tokens = word_tokenize(
        no_punct.lower()
    )

    filtered_tokens = [
        token
        for token in tokens
        if token not in stop_words
    ]

    lemmatized = [
        lemmatizer.lemmatize(token)
        for token in filtered_tokens
    ]

    final_text = " ".join(
        lemmatized
    )

    return {
        "final_processed_text": final_text,
        "tokens": tokens,
        "lemmatized": lemmatized
    }


# ============================================================
# 10. SENTIMENT ANALYSIS
# ============================================================

def analyze_sentiment(text):

    scores = sia.polarity_scores(
        text
    )

    compound = scores["compound"]

    if compound >= 0.05:

        label = "Positive"

    elif compound <= -0.05:

        label = "Negative"

    else:

        label = "Neutral"

    return {
        "positive": scores["pos"],
        "negative": scores["neg"],
        "neutral": scores["neu"],
        "compound": compound,
        "label": label
    }


# ============================================================
# 11. EMOTION DETECTION
# ============================================================

def detect_emotion(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = emotion_model(
            **inputs
        )

    probabilities = torch.sigmoid(
        outputs.logits
    )[0]

    probabilities = probabilities.tolist()

    emotion_scores = {}

    for index, emotion in enumerate(
        EMOTION_LABELS
    ):

        emotion_scores[emotion] = (
            probabilities[index]
        )

    dominant_emotion = max(
        emotion_scores,
        key=emotion_scores.get
    )

    confidence = emotion_scores[
        dominant_emotion
    ]

    return {
        "scores": emotion_scores,
        "dominant_emotion": dominant_emotion,
        "confidence": confidence
    }


# ============================================================
# 12. EMOTION INTENSITY
# ============================================================

def calculate_intensity(
    confidence
):

    if confidence >= 0.70:

        return "High"

    elif confidence >= 0.40:

        return "Medium"

    return "Low"


# ============================================================
# 13. SAVE EMOTIONAL HISTORY
# ============================================================

def save_emotional_history(
    user_id,
    text,
    emotion,
    confidence,
    intensity,
    sentiment
):

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO emotional_history
        (
            user_id,
            text,
            emotion,
            confidence,
            intensity,
            sentiment,
            timestamp
        )
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (
            user_id,
            text,
            emotion,
            confidence,
            intensity,
            sentiment
        )
    )

    connection.commit()
    connection.close()

# ============================================================
# 14. LOAD HYBRID DATA
# ============================================================

@st.cache_data
def load_hybrid_data():

    return pd.read_csv(
        HYBRID_FILE
    )


hybrid_df = load_hybrid_data()


# ============================================================
# 15. HYBRID RECOMMENDATION
# ============================================================

def generate_hybrid_recommendations(
    emotion,
    intensity,
    preference,
    previous_interaction,
    recommendation_history
):

    results = []

    for _, row in hybrid_df.iterrows():

        score = 0

        if row["emotion"] == emotion:

            score += 3

        if row["intensity"] == intensity:

            score += 2

        if row["preference"] == preference:

            score += 2

        if (
            row["previous_interaction"]
            == previous_interaction
        ):

            score += 1

        if (
            row["recommendation_history"]
            == recommendation_history
        ):

            score += 1

        results.append(
            {
                "recommendation":
                    row["recommendation"],
                "hybrid_score":
                    score
            }
        )

    result_df = pd.DataFrame(
        results
    )

    result_df = result_df.sort_values(
        "hybrid_score",
        ascending=False
    )

    result_df = result_df.drop_duplicates(
        subset=["recommendation"]
    )

    return result_df.reset_index(
        drop=True
    )


# ============================================================
# 16. LOAD WELLNESS CONTENT
# ============================================================

@st.cache_data
def load_wellness_data():

    return pd.read_csv(
        WELLNESS_FILE
    )


wellness_df = load_wellness_data()


# ============================================================
# 17. SEMANTIC MATCHING
# ============================================================

def semantic_matching(text):

    query_embedding = semantic_model.encode(
        text,
        convert_to_tensor=True
    )

    content_embeddings = semantic_model.encode(
        wellness_df["content"].tolist(),
        convert_to_tensor=True
    )

    similarities = util.cos_sim(
        query_embedding,
        content_embeddings
    )[0]

    result = wellness_df.copy()

    result["semantic_score"] = [
        float(score)
        for score in similarities
    ]

    result = result.sort_values(
        "semantic_score",
        ascending=False
    )

    return result.reset_index(
        drop=True
    )


# ============================================================
# 18. FINAL RECOMMENDATION RANKING
# ============================================================

def rank_final_recommendations(
    hybrid_results,
    semantic_results
):

    final_results = hybrid_results.copy()

    if not semantic_results.empty:

        semantic_score = (
            semantic_results[
                "semantic_score"
            ].max()
        )

    else:

        semantic_score = 0.0

    final_results[
        "semantic_score"
    ] = semantic_score

    final_results[
        "final_score"
    ] = (
        final_results[
            "hybrid_score"
        ] * 0.7
        +
        final_results[
            "semantic_score"
        ] * 10 * 0.3
    )

    final_results = final_results.sort_values(
        "final_score",
        ascending=False
    )

    return final_results.reset_index(
        drop=True
    )


# ============================================================
# 19. SAVE FEEDBACK
# ============================================================

def save_feedback(
    user_id,
    recommendation,
    accepted,
    rating
):

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO feedback
        (
            user_id,
            recommendation,
            accepted,
            rating
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            user_id,
            recommendation,
            accepted,
            rating
        )
    )

    connection.commit()
    connection.close()


# ============================================================
# 20. LOAD EMOTIONAL HISTORY
# ============================================================

def load_emotional_history():

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    history_df = pd.read_sql_query(
        """
        SELECT
            id,
            user_id,
            text,
            emotion,
            confidence,
            intensity,
            sentiment
        FROM emotional_history
        ORDER BY id DESC
        """,
        connection
    )

    connection.close()

    return history_df


# ============================================================
# 21. ADVANCED DASHBOARD
# ============================================================

def display_dashboard(
    emotion_result,
    sentiment,
    intensity,
    recommendation
):

    st.divider()

    st.header(
        "📊 Emotional Wellness Dashboard"
    )

    emotion = emotion_result[
        "dominant_emotion"
    ]

    confidence = emotion_result[
        "confidence"
    ]

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Dominant Emotion",
            emotion.capitalize()
        )

    with col2:

        st.metric(
            "Confidence",
            f"{confidence * 100:.1f}%"
        )

    with col3:

        st.metric(
            "Intensity",
            intensity
        )

    with col4:

        st.metric(
            "Sentiment",
            sentiment["label"]
        )

    st.subheader(
        "📈 Emotion Scores"
    )

    score_df = pd.DataFrame(
        {
            "Emotion":
                list(
                    emotion_result[
                        "scores"
                    ].keys()
                ),
            "Score":
                [
                    value * 100
                    for value in
                    emotion_result[
                        "scores"
                    ].values()
                ]
        }
    )

    st.bar_chart(
        score_df.set_index(
            "Emotion"
        )
    )

    st.dataframe(
        score_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "💡 Personalized Wellness Recommendation"
    )

    st.success(
        recommendation
    )


# ============================================================
# 22. EMOTIONAL HISTORY DASHBOARD
# ============================================================

def display_history_dashboard(
    user_id
):

    st.divider()

    st.header(
        "📜 User Emotional History"
    )

    history_df = load_emotional_history()

    if history_df.empty:

        st.info(
            "No emotional history available yet."
        )

        return

    user_history = history_df[
        history_df["user_id"] == user_id
    ].copy()

    if user_history.empty:

        st.info(
            "No history available for this user yet."
        )

        return

    user_history[
        "confidence_percentage"
    ] = (
        user_history["confidence"] * 100
    ).round(2)

    display_df = user_history[
        [
            "id",
            "emotion",
            "confidence_percentage",
            "intensity",
            "sentiment"
        ]
    ].copy()

    display_df = display_df.rename(
        columns={
            "confidence_percentage":
                "Confidence (%)"
        }
    )

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader(
        "Emotion Frequency"
    )

    emotion_counts = (
        user_history["emotion"]
        .value_counts()
    )

    st.bar_chart(
        emotion_counts
    )


# ============================================================
# 23. USER INPUT
# ============================================================

st.header(
    "📝 User Input"
)

user_id = st.text_input(
    "User ID",
    value="U1"
)

text_input = st.text_area(
    "Enter your current thoughts or feelings:",
    height=150
)

col1, col2, col3 = st.columns(3)

with col1:

    preference = st.selectbox(
        "Wellness preference",
        [
            "meditation",
            "music",
            "physical activity",
            "writing",
            "activity"
        ]
    )

with col2:

    previous_interaction = st.selectbox(
        "Previous interaction",
        [
            "breathing",
            "meditation",
            "music",
            "walking",
            "exercise",
            "journaling"
        ]
    )

with col3:

    recommendation_history = st.selectbox(
        "Recommendation history",
        [
            "breathing",
            "meditation",
            "music",
            "walking",
            "exercise",
            "journaling"
        ]
    )


# ============================================================
# 24. RUN WORKFLOW
# ============================================================

if st.button(
    "🧠 Analyze My Emotional State",
    use_container_width=True
):

    if not validate_text(text_input):

        st.warning(
            "Please enter some text first."
        )

    else:

        try:

            # ------------------------------------------------
            # PREPROCESSING
            # ------------------------------------------------

            preprocessing_result = preprocess(
                text_input
            )

            st.subheader(
                "🔤 Preprocessed Text"
            )

            st.info(
                preprocessing_result[
                    "final_processed_text"
                ]
            )


            # ------------------------------------------------
            # SENTIMENT
            # ------------------------------------------------

            sentiment = analyze_sentiment(
                text_input
            )


            # ------------------------------------------------
            # EMOTION
            # ------------------------------------------------

            emotion_result = detect_emotion(
                text_input
            )

            emotion = emotion_result[
                "dominant_emotion"
            ]

            confidence = emotion_result[
                "confidence"
            ]


            # ------------------------------------------------
            # INTENSITY
            # ------------------------------------------------

            intensity = calculate_intensity(
                confidence
            )


            # ------------------------------------------------
            # SAVE HISTORY
            # ------------------------------------------------

            save_emotional_history(
                user_id,
                text_input,
                emotion,
                confidence,
                intensity,
                sentiment["label"]
            )


            # ------------------------------------------------
            # HYBRID RECOMMENDATIONS
            # ------------------------------------------------

            hybrid_results = (
                generate_hybrid_recommendations(
                    emotion,
                    intensity,
                    preference,
                    previous_interaction,
                    recommendation_history
                )
            )


            # ------------------------------------------------
            # SEMANTIC MATCHING
            # ------------------------------------------------

            semantic_results = semantic_matching(
                text_input
            )


            # ------------------------------------------------
            # FINAL RANKING
            # ------------------------------------------------

            final_results = (
                rank_final_recommendations(
                    hybrid_results,
                    semantic_results
                )
            )


            if final_results.empty:

                st.warning(
                    "No recommendation was generated."
                )

            else:

                final_recommendation = (
                    final_results.iloc[0][
                        "recommendation"
                    ]
                )

                # Store result
                st.session_state[
                    "last_recommendation"
                ] = final_recommendation

                st.session_state[
                    "workflow_completed"
                ] = True

                st.session_state[
                    "last_user_id"
                ] = user_id

                # ------------------------------------------------
                # ADVANCED DASHBOARD
                # ------------------------------------------------

                display_dashboard(
                    emotion_result,
                    sentiment,
                    intensity,
                    final_recommendation
                )

                # ------------------------------------------------
                # RECOMMENDATION DETAILS
                # ------------------------------------------------

                st.subheader(
                    "🏆 Recommendation Ranking"
                )

                st.dataframe(
                    final_results[
                        [
                            "recommendation",
                            "hybrid_score",
                            "semantic_score",
                            "final_score"
                        ]
                    ].head(5),
                    use_container_width=True,
                    hide_index=True
                )

                # ------------------------------------------------
                # SEMANTIC CONTENT
                # ------------------------------------------------

                st.subheader(
                    "🔎 Related Wellness Content"
                )

                if not semantic_results.empty:

                    columns = [
                        "title",
                        "emotion",
                        "semantic_score"
                    ]

                    available_columns = [
                        column
                        for column in columns
                        if column in
                        semantic_results.columns
                    ]

                    st.dataframe(
                        semantic_results[
                            available_columns
                        ].head(5),
                        use_container_width=True,
                        hide_index=True
                    )


                # ------------------------------------------------
                # HISTORY
                # ------------------------------------------------

                display_history_dashboard(
                    user_id
                )

        except Exception as error:

            st.error(
                "An error occurred while "
                "processing the workflow."
            )

            st.exception(error)


# ============================================================
# 25. FEEDBACK
# ============================================================

if st.session_state.get(
    "workflow_completed",
    False
):

    st.divider()

    st.header(
        "⭐ Recommendation Feedback"
    )

    feedback_choice = st.radio(
        "Did you accept this recommendation?",
        ["Yes", "No"],
        horizontal=True
    )

    rating = st.slider(
        "Rate the recommendation",
        min_value=1,
        max_value=5,
        value=3
    )

    if st.button(
        "Save Feedback"
    ):

        save_feedback(
            st.session_state[
                "last_user_id"
            ],
            st.session_state[
                "last_recommendation"
            ],
            feedback_choice,
            rating
        )

        st.success(
            "Feedback saved successfully."
        )


# ============================================================
# 26. STORED FEEDBACK
# ============================================================

st.divider()

st.header(
    "📋 Stored Feedback"
)

try:

    connection = sqlite3.connect(
        DATABASE_FILE
    )

    feedback_df = pd.read_sql_query(
        "SELECT * FROM feedback ORDER BY id DESC",
        connection
    )

    connection.close()

    if feedback_df.empty:

        st.info(
            "No feedback has been stored yet."
        )

    else:

        st.dataframe(
            feedback_df,
            use_container_width=True,
            hide_index=True
        )

except Exception as error:

    st.error(
        f"Could not read feedback database: {error}"
    )


# ============================================================
# 27. TASK 1 CHECK
# ============================================================

st.divider()

st.caption(
    "Milestone 4 – Task 1: Advanced Streamlit Dashboard"
)

