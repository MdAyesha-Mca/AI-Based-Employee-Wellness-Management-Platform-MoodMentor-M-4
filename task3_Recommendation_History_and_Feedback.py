import os
import sqlite3
import pandas as pd
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MoodMentor - Recommendation History",
    page_icon="⭐",
    layout="wide"
)


# =========================================================
# PATH
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MILESTONE3_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "milestone3")
)

DATABASE_FILE = os.path.join(
    MILESTONE3_DIR,
    "moodmentor.db"
)


# =========================================================
# TITLE
# =========================================================

st.title(
    "⭐ MoodMentor - Recommendation History & Feedback"
)

st.write(
    "View previous wellness recommendations and submit feedback."
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return sqlite3.connect(
        DATABASE_FILE
    )


# =========================================================
# CREATE FEEDBACK TABLE IF REQUIRED
# =========================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

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


# =========================================================
# LOAD RECOMMENDATION HISTORY
# =========================================================

def load_recommendation_history():

    connection = get_connection()

    try:

        # Check whether emotional history exists
        tables = pd.read_sql_query(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            """,
            connection
        )

        table_names = tables["name"].tolist()

        if "emotional_history" not in table_names:

            return pd.DataFrame()

        df = pd.read_sql_query(
            """
            SELECT
                id,
                user_id,
                emotion,
                confidence,
                intensity,
                sentiment
            FROM emotional_history
            ORDER BY id DESC
            """,
            connection
        )

        return df

    except Exception as error:

        st.error(
            f"Could not load recommendation history: {error}"
        )

        return pd.DataFrame()

    finally:

        connection.close()


# =========================================================
# LOAD FEEDBACK HISTORY
# =========================================================

def load_feedback_history():

    connection = get_connection()

    try:

        df = pd.read_sql_query(
            """
            SELECT
                id,
                user_id,
                recommendation,
                accepted,
                rating
            FROM feedback
            ORDER BY id DESC
            """,
            connection
        )

        return df

    except Exception as error:

        st.error(
            f"Could not load feedback history: {error}"
        )

        return pd.DataFrame()

    finally:

        connection.close()


# =========================================================
# SAVE FEEDBACK
# =========================================================

def save_feedback(
    user_id,
    recommendation,
    accepted,
    rating
):

    connection = get_connection()

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


# =========================================================
# USER INFORMATION
# =========================================================

st.header("👤 User Information")

user_id = st.text_input(
    "User ID",
    value="U1"
)


# =========================================================
# RECOMMENDATION INPUT
# =========================================================

st.header("💡 Current Recommendation")

recommendation = st.text_area(
    "Recommendation",
    value="Try a guided breathing exercise.",
    height=100
)


# =========================================================
# DISPLAY CURRENT RECOMMENDATION
# =========================================================

st.success(
    recommendation
)


# =========================================================
# FEEDBACK SECTION
# =========================================================

st.header("⭐ Submit Feedback")

accepted = st.radio(
    "Did you find this recommendation useful?",
    [
        "Yes",
        "No"
    ],
    horizontal=True
)

rating = st.slider(
    "Rate this recommendation",
    min_value=1,
    max_value=5,
    value=3
)


if st.button(
    "💾 Save Feedback"
):

    if not recommendation.strip():

        st.error(
            "Please enter a recommendation."
        )

    else:

        save_feedback(
            user_id,
            recommendation,
            accepted,
            rating
        )

        st.success(
            "Feedback saved successfully!"
        )


# =========================================================
# RECOMMENDATION HISTORY
# =========================================================

st.divider()

st.header(
    "📜 Recommendation / Emotional History"
)

history_df = load_recommendation_history()


if history_df.empty:

    st.info(
        "No recommendation history is available yet."
    )

else:

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FEEDBACK HISTORY
# =========================================================

st.header(
    "📋 Feedback History"
)

feedback_df = load_feedback_history()


if feedback_df.empty:

    st.info(
        "No feedback has been submitted yet."
    )

else:

    st.dataframe(
        feedback_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FEEDBACK SUMMARY
# =========================================================

if not feedback_df.empty:

    st.header(
        "📊 Feedback Summary"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Feedback",
            len(feedback_df)
        )

    with col2:

        average_rating = (
            feedback_df["rating"]
            .mean()
        )

        st.metric(
            "Average Rating",
            f"{average_rating:.2f}/5"
        )

    with col3:

        accepted_count = (
            feedback_df["accepted"]
            .eq("Yes")
            .sum()
        )

        st.metric(
            "Accepted Recommendations",
            accepted_count
        )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "MoodMentor | Milestone 4 - Task 3 "
    "Recommendation History and Feedback"
)