import os
import sqlite3
import pandas as pd
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MoodMentor - Advanced Search & Filtering",
    page_icon="🔎",
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

st.title("🔎 MoodMentor - Advanced Search & Filtering")

st.write(
    "Search and filter emotional records, recommendations, "
    "and feedback."
)


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_connection():

    return sqlite3.connect(
        DATABASE_FILE
    )


# =========================================================
# LOAD EMOTIONAL RECORDS
# =========================================================

def load_emotional_records():

    connection = get_connection()

    try:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM emotional_history
            ORDER BY id DESC
            """,
            connection
        )

        return df

    except Exception as error:

        st.error(
            f"Could not load emotional records: {error}"
        )

        return pd.DataFrame()

    finally:

        connection.close()


# =========================================================
# LOAD FEEDBACK
# =========================================================

def load_feedback():

    connection = get_connection()

    try:

        df = pd.read_sql_query(
            """
            SELECT *
            FROM feedback
            ORDER BY id DESC
            """,
            connection
        )

        return df

    except Exception as error:

        st.error(
            f"Could not load feedback: {error}"
        )

        return pd.DataFrame()

    finally:

        connection.close()


# =========================================================
# LOAD DATA
# =========================================================

emotional_df = load_emotional_records()

feedback_df = load_feedback()


# =========================================================
# CHECK DATABASE
# =========================================================

if emotional_df.empty:

    st.warning(
        "No emotional records are available yet."
    )

    st.info(
        "Run Task 1 and analyze some text first."
    )

    st.stop()


# =========================================================
# PREPARE DATE
# =========================================================

if "timestamp" in emotional_df.columns:

    emotional_df["timestamp"] = pd.to_datetime(
        emotional_df["timestamp"],
        errors="coerce"
    )

    emotional_df["date"] = (
        emotional_df["timestamp"]
        .dt.date
    )

else:

    emotional_df["date"] = pd.NaT


# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("🔎 Search & Filters")


# =========================================================
# TEXT SEARCH
# =========================================================

search_text = st.sidebar.text_input(
    "Search text",
    placeholder="Enter keyword..."
)


# =========================================================
# DATE FILTER
# =========================================================

st.sidebar.subheader("📅 Date Filter")

valid_dates = emotional_df["date"].dropna()

if not valid_dates.empty:

    min_date = valid_dates.min()
    max_date = valid_dates.max()

    selected_date_range = st.sidebar.date_input(
        "Select date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

else:

    selected_date_range = None


# =========================================================
# EMOTION FILTER
# =========================================================

st.sidebar.subheader("😊 Emotion")

emotion_options = sorted(
    emotional_df["emotion"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_emotions = st.sidebar.multiselect(
    "Select emotion",
    emotion_options
)


# =========================================================
# INTENSITY FILTER
# =========================================================

st.sidebar.subheader("⚡ Intensity")

if "intensity" in emotional_df.columns:

    intensity_options = sorted(
        emotional_df["intensity"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:

    intensity_options = []


selected_intensity = st.sidebar.multiselect(
    "Select intensity",
    intensity_options
)


# =========================================================
# RECOMMENDATION TYPE FILTER
# =========================================================

st.sidebar.subheader("💡 Recommendation Type")

if not feedback_df.empty and "recommendation" in feedback_df.columns:

    recommendation_options = sorted(
        feedback_df["recommendation"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

else:

    recommendation_options = []


selected_recommendations = st.sidebar.multiselect(
    "Select recommendation",
    recommendation_options
)


# =========================================================
# FEEDBACK STATUS FILTER
# =========================================================

st.sidebar.subheader("⭐ Feedback Status")

feedback_status_options = [
    "All",
    "Yes",
    "No"
]

selected_feedback_status = st.sidebar.selectbox(
    "Select feedback status",
    feedback_status_options
)


# =========================================================
# APPLY EMOTIONAL FILTERS
# =========================================================

filtered_emotional = emotional_df.copy()


# ---------------------------------------------------------
# SEARCH
# ---------------------------------------------------------

if search_text:

    search_mask = (
        filtered_emotional["text"]
        .astype(str)
        .str.contains(
            search_text,
            case=False,
            na=False
        )
    )

    filtered_emotional = (
        filtered_emotional[
            search_mask
        ]
    )


# ---------------------------------------------------------
# DATE
# ---------------------------------------------------------

if (
    selected_date_range
    and len(selected_date_range) == 2
):

    start_date = selected_date_range[0]
    end_date = selected_date_range[1]

    filtered_emotional = filtered_emotional[
        (
            filtered_emotional["date"]
            >= start_date
        )
        &
        (
            filtered_emotional["date"]
            <= end_date
        )
    ]


# ---------------------------------------------------------
# EMOTION
# ---------------------------------------------------------

if selected_emotions:

    filtered_emotional = filtered_emotional[
        filtered_emotional["emotion"]
        .isin(selected_emotions)
    ]


# ---------------------------------------------------------
# INTENSITY
# ---------------------------------------------------------

if selected_intensity:

    filtered_emotional = filtered_emotional[
        filtered_emotional["intensity"]
        .astype(str)
        .isin(selected_intensity)
    ]


# =========================================================
# APPLY FEEDBACK FILTER
# =========================================================

filtered_feedback = feedback_df.copy()


if selected_feedback_status != "All":

    if not filtered_feedback.empty:

        filtered_feedback = filtered_feedback[
            filtered_feedback["accepted"]
            .astype(str)
            == selected_feedback_status
        ]


# =========================================================
# RECOMMENDATION FILTER
# =========================================================

if selected_recommendations:

    if not filtered_feedback.empty:

        filtered_feedback = filtered_feedback[
            filtered_feedback[
                "recommendation"
            ]
            .astype(str)
            .isin(selected_recommendations)
        ]


# =========================================================
# DISPLAY RESULTS
# =========================================================

st.header("📊 Filtered Results")


# =========================================================
# RESULT COUNTS
# =========================================================

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Matching Emotional Records",
        len(filtered_emotional)
    )

with col2:

    st.metric(
        "Matching Feedback Records",
        len(filtered_feedback)
    )


# =========================================================
# EMOTIONAL RECORDS
# =========================================================

st.subheader(
    "🧠 Matching Emotional Records"
)

if filtered_emotional.empty:

    st.info(
        "No emotional records match the selected filters."
    )

else:

    display_columns = [
        column
        for column in [
            "id",
            "user_id",
            "text",
            "emotion",
            "confidence",
            "intensity",
            "sentiment",
            "timestamp"
        ]
        if column in filtered_emotional.columns
    ]

    st.dataframe(
        filtered_emotional[
            display_columns
        ],
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# RECOMMENDATION RESULTS
# =========================================================

st.subheader(
    "💡 Matching Recommendations"
)

if filtered_feedback.empty:

    st.info(
        "No recommendations match the selected filters."
    )

else:

    st.dataframe(
        filtered_feedback,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# FEEDBACK STATUS SUMMARY
# =========================================================

st.subheader(
    "⭐ Feedback Status"
)

if not filtered_feedback.empty:

    status_counts = (
        filtered_feedback["accepted"]
        .value_counts()
    )

    st.bar_chart(
        status_counts
    )

else:

    st.info(
        "No feedback data available for the selected filters."
    )


# =========================================================
# CLEAR FILTER INFORMATION
# =========================================================

st.divider()

st.caption(
    "Use the filters in the sidebar to dynamically search "
    "and retrieve matching MoodMentor records."
)


# =========================================================
# DOWNLOAD FILTERED DATA
# =========================================================

if not filtered_emotional.empty:

    csv_data = filtered_emotional.to_csv(
        index=False
    )

    st.download_button(
        label="⬇️ Download Filtered Emotional Records",
        data=csv_data,
        file_name="filtered_emotional_records.csv",
        mime="text/csv"
    )