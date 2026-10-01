import os
import sqlite3
import pandas as pd
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="MoodMentor - Emotional Trend Visualization",
    page_icon="📈",
    layout="wide"
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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

st.title("📈 MoodMentor - Emotional Trend Visualization")

st.write(
    "Track changes in emotional state using stored emotional history."
)


# =========================================================
# LOAD EMOTIONAL HISTORY
# =========================================================

def load_emotional_history():

    conn = sqlite3.connect(DATABASE_FILE)

    try:

        # Check existing database columns
        columns = pd.read_sql_query(
            "PRAGMA table_info(emotional_history)",
            conn
        )

        column_names = columns["name"].tolist()

        # Add timestamp if it does not exist
        if "timestamp" not in column_names:

            conn.execute(
                "ALTER TABLE emotional_history ADD COLUMN timestamp TEXT"
            )

            # Give existing records a timestamp
            conn.execute("""
                UPDATE emotional_history
                SET timestamp = datetime('now')
                WHERE timestamp IS NULL
            """)

            conn.commit()

        # Load data
        df = pd.read_sql_query(
            """
            SELECT
                id,
                user_id,
                text,
                emotion,
                confidence,
                intensity,
                sentiment,
                timestamp
            FROM emotional_history
            ORDER BY timestamp
            """,
            conn
        )

        return df

    except Exception as e:

        st.error(
            f"Unable to load emotional history: {e}"
        )

        return pd.DataFrame()

    finally:

        conn.close()


# =========================================================
# PREPARE DATA
# =========================================================

def prepare_data(df):

    if df.empty:
        return df

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # Remove invalid timestamps
    df = df.dropna(
        subset=["timestamp"]
    )

    # Convert numerical columns
    for column in ["confidence", "intensity"]:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    return df


# =========================================================
# DAILY TREND
# =========================================================

def calculate_daily_trend(df):

    if df.empty:
        return pd.DataFrame()

    daily = (
        df.set_index("timestamp")
        .resample("D")
        .agg(
            average_intensity=("intensity", "mean"),
            average_confidence=("confidence", "mean"),
            emotion_count=("emotion", "count")
        )
        .reset_index()
    )

    return daily


# =========================================================
# WEEKLY TREND
# =========================================================

def calculate_weekly_trend(df):

    if df.empty:
        return pd.DataFrame()

    weekly = (
        df.set_index("timestamp")
        .resample("W")
        .agg(
            average_intensity=("intensity", "mean"),
            average_confidence=("confidence", "mean"),
            emotion_count=("emotion", "count")
        )
        .reset_index()
    )

    return weekly


# =========================================================
# MONTHLY TREND
# =========================================================

def calculate_monthly_trend(df):

    if df.empty:
        return pd.DataFrame()

    monthly = (
        df.set_index("timestamp")
        .resample("ME")
        .agg(
            average_intensity=("intensity", "mean"),
            average_confidence=("confidence", "mean"),
            emotion_count=("emotion", "count")
        )
        .reset_index()
    )

    return monthly


# =========================================================
# LOAD DATA
# =========================================================

history_df = load_emotional_history()

history_df = prepare_data(history_df)


# =========================================================
# CHECK DATA
# =========================================================

if history_df.empty:

    st.warning(
        "No emotional history is available yet."
    )

    st.info(
        "Run Task 1 and analyze some text first."
    )

    st.stop()


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("🔎 Filters")

users = history_df["user_id"].dropna().unique().tolist()

selected_user = st.sidebar.selectbox(
    "Select User",
    ["All Users"] + list(users)
)


# =========================================================
# APPLY USER FILTER
# =========================================================

if selected_user != "All Users":

    filtered_df = history_df[
        history_df["user_id"] == selected_user
    ].copy()

else:

    filtered_df = history_df.copy()


# =========================================================
# CHECK FILTERED DATA
# =========================================================

if filtered_df.empty:

    st.warning(
        "No emotional records found for this user."
    )

    st.stop()


# =========================================================
# SUMMARY METRICS
# =========================================================

st.subheader("📊 Emotional Summary")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Total Records",
        len(filtered_df)
    )

with col2:

    most_common_emotion = (
        filtered_df["emotion"]
        .value_counts()
        .idxmax()
    )

    st.metric(
        "Most Frequent Emotion",
        most_common_emotion
    )

with col3:

    average_intensity = (
        filtered_df["intensity"]
        .mean()
    )

    st.metric(
        "Average Intensity",
        f"{average_intensity:.2f}"
    )


# =========================================================
# STORED EMOTIONAL DATA
# =========================================================

st.subheader("🗂️ Stored Emotional History")

display_columns = [
    "id",
    "user_id",
    "text",
    "emotion",
    "confidence",
    "intensity",
    "sentiment",
    "timestamp"
]

available_columns = [
    column
    for column in display_columns
    if column in filtered_df.columns
]

st.dataframe(
    filtered_df[available_columns],
    use_container_width=True
)


# =========================================================
# TREND SELECTION
# =========================================================

st.subheader("📈 Emotional Trends")

trend_type = st.radio(
    "Select Trend Period",
    [
        "Daily",
        "Weekly",
        "Monthly"
    ],
    horizontal=True
)


# =========================================================
# CALCULATE SELECTED TREND
# =========================================================

if trend_type == "Daily":

    trend_df = calculate_daily_trend(
        filtered_df
    )

elif trend_type == "Weekly":

    trend_df = calculate_weekly_trend(
        filtered_df
    )

else:

    trend_df = calculate_monthly_trend(
        filtered_df
    )


# =========================================================
# TREND CHART
# =========================================================

if not trend_df.empty:

    chart_df = trend_df.set_index(
        "timestamp"
    )

    st.line_chart(
        chart_df[
            [
                "average_intensity",
                "average_confidence"
            ]
        ]
    )

    st.subheader(
        f"{trend_type} Trend Data"
    )

    st.dataframe(
        trend_df,
        use_container_width=True
    )

else:

    st.info(
        f"No {trend_type.lower()} trend data available."
    )


# =========================================================
# EMOTION DISTRIBUTION
# =========================================================

st.subheader("😊 Emotion Distribution")

emotion_counts = (
    filtered_df["emotion"]
    .value_counts()
)

st.bar_chart(
    emotion_counts
)


# =========================================================
# EMOTION SUMMARY
# =========================================================

st.subheader("🧠 Emotion Insights")

for emotion, count in emotion_counts.items():

    percentage = (
        count / len(filtered_df)
    ) * 100

    st.write(
        f"**{emotion}**: "
        f"{count} record(s) "
        f"({percentage:.1f}%)"
    )


# =========================================================
# DOWNLOAD DATA
# =========================================================

csv_data = filtered_df.to_csv(
    index=False
)

st.download_button(
    label="⬇️ Download Emotional History",
    data=csv_data,
    file_name="emotional_history.csv",
    mime="text/csv"
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "MoodMentor | Milestone 4 - Task 2 "
    "Emotional Trend Visualization"
)