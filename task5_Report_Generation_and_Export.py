import streamlit as st
import sqlite3
import pandas as pd
from io import BytesIO

# PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MoodMentor - Report Generation",
    page_icon="📊",
    layout="wide"
)

DATABASE_FILE = "../milestone3/moodmentor.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_FILE)


# ============================================================
# LOAD EMOTIONAL HISTORY
# ============================================================

def load_emotional_history():
    connection = get_connection()

    query = """
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
    """

    df = pd.read_sql_query(query, connection)

    connection.close()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(
            df["timestamp"],
            errors="coerce"
        )

        df["confidence"] = pd.to_numeric(
            df["confidence"],
            errors="coerce"
        )

        df["intensity"] = df["intensity"].astype(str)

    return df


# ============================================================
# LOAD FEEDBACK / RECOMMENDATIONS
# ============================================================

def load_feedback():
    connection = get_connection()

    query = """
        SELECT
            id,
            user_id,
            recommendation,
            accepted,
            rating
        FROM feedback
        ORDER BY id
    """

    df = pd.read_sql_query(query, connection)

    connection.close()

    return df


# ============================================================
# GENERATE CSV REPORT
# ============================================================

def create_csv_report(emotional_data, feedback_data):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        emotional_data.to_excel(
            writer,
            index=False,
            sheet_name="Emotional Analysis"
        )

        feedback_data.to_excel(
            writer,
            index=False,
            sheet_name="Recommendations"

        )

        # Generate trend data
        if not emotional_data.empty:

            trend_data = (
                emotional_data
                .set_index("timestamp")
                .resample("D")
                .agg(
                    Records=("id", "count"),
                    Average_Confidence=("confidence", "mean")
                )
                .reset_index()
            )

        else:

            trend_data = pd.DataFrame(
                columns=[
                    "timestamp",
                    "Records",
                    "Average_Confidence"
                ]
            )

        trend_data.to_excel(
            writer,
            index=False,
            sheet_name="Daily Trends"
        )

    output.seek(0)

    return output


# ============================================================
# GENERATE PDF REPORT
# ============================================================

def create_pdf_report(emotional_data, feedback_data):

    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    title_style.alignment = TA_CENTER

    heading_style = styles["Heading2"]
    normal_style = styles["BodyText"]

    elements = []

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "MoodMentor Emotional Wellness Report",
            title_style
        )
    )

    elements.append(Spacer(1, 15))

    # --------------------------------------------------------
    # DATE RANGE
    # --------------------------------------------------------

    if not emotional_data.empty:

        start_date = emotional_data["timestamp"].min()
        end_date = emotional_data["timestamp"].max()

        date_text = (
            f"Report Period: "
            f"{start_date.strftime('%Y-%m-%d')} "
            f"to "
            f"{end_date.strftime('%Y-%m-%d')}"
        )

    else:

        date_text = "Report Period: No data available"

    elements.append(
        Paragraph(date_text, normal_style)
    )

    elements.append(Spacer(1, 15))

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "Emotional Analysis Summary",
            heading_style
        )
    )

    total_records = len(emotional_data)

    if not emotional_data.empty:

        most_frequent_emotion = (
            emotional_data["emotion"]
            .value_counts()
            .idxmax()
        )

        average_confidence = (
            emotional_data["confidence"]
            .mean()
        )

    else:

        most_frequent_emotion = "No data"
        average_confidence = 0

    summary_data = [
        ["Metric", "Value"],
        ["Total Emotional Records", str(total_records)],
        ["Most Frequent Emotion", str(most_frequent_emotion)],
        [
            "Average Confidence",
            f"{average_confidence:.2f}%"
        ]
    ]

    summary_table = Table(summary_data)

    summary_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("PADDING", (0, 0), (-1, -1), 5)
        ])
    )

    elements.append(summary_table)

    elements.append(Spacer(1, 20))

    # --------------------------------------------------------
    # EMOTIONAL RECORDS
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "Emotional Analysis Records",
            heading_style
        )
    )

    if not emotional_data.empty:

        table_data = [
            [
                "Date",
                "Emotion",
                "Confidence",
                "Intensity",
                "Sentiment"
            ]
        ]

        for _, row in emotional_data.iterrows():

            date_value = row["timestamp"]

            if pd.notna(date_value):
                date_value = date_value.strftime(
                    "%Y-%m-%d"
                )
            else:
                date_value = "N/A"

            confidence_value = row["confidence"]

            if pd.notna(confidence_value):
                confidence_text = (
                    f"{confidence_value:.2f}"
                )
            else:
                confidence_text = "N/A"

            table_data.append([
                date_value,
                str(row["emotion"]),
                confidence_text,
                str(row["intensity"]),
                str(row["sentiment"])
            ])

        emotion_table = Table(
            table_data,
            repeatRows=1
        )

        emotion_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("PADDING", (0, 0), (-1, -1), 4),
                ("FONTSIZE", (0, 0), (-1, -1), 8)
            ])
        )

        elements.append(emotion_table)

    else:

        elements.append(
            Paragraph(
                "No emotional analysis data available.",
                normal_style
            )
        )

    elements.append(Spacer(1, 20))

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    elements.append(
        Paragraph(
            "Recommendations and Feedback",
            heading_style
        )
    )

    if not feedback_data.empty:

        recommendation_table = [
            [
                "Recommendation",
                "Accepted",
                "Rating"
            ]
        ]

        for _, row in feedback_data.iterrows():

            recommendation_table.append([
                str(row["recommendation"]),
                str(row["accepted"]),
                str(row["rating"])
            ])

        feedback_table = Table(
            recommendation_table,
            repeatRows=1
        )

        feedback_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ("PADDING", (0, 0), (-1, -1), 5),
                ("FONTSIZE", (0, 0), (-1, -1), 8)
            ])
        )

        elements.append(feedback_table)

    else:

        elements.append(
            Paragraph(
                "No recommendation feedback available.",
                normal_style
            )
        )

    # --------------------------------------------------------
    # BUILD PDF
    # --------------------------------------------------------

    document.build(elements)

    output.seek(0)

    return output


# ============================================================
# STREAMLIT UI
# ============================================================

st.title("📊 MoodMentor - Report Generation and Export")

st.write(
    "Generate downloadable reports containing emotional "
    "analysis, trends, and recommendations."
)


# ============================================================
# LOAD DATA
# ============================================================

emotional_history = load_emotional_history()
feedback_data = load_feedback()


if emotional_history.empty:

    st.warning(
        "No emotional history data is available."
    )

    st.stop()


# ============================================================
# DATE RANGE FILTER
# ============================================================

st.sidebar.header("📅 Select Date Range")

valid_dates = emotional_history["timestamp"].dropna()

if valid_dates.empty:

    st.error(
        "No valid timestamps are available."
    )

    st.stop()


min_date = valid_dates.min().date()
max_date = valid_dates.max().date()


start_date = st.sidebar.date_input(
    "Start Date",
    value=min_date,
    min_value=min_date,
    max_value=max_date
)

end_date = st.sidebar.date_input(
    "End Date",
    value=max_date,
    min_value=min_date,
    max_value=max_date
)


# ============================================================
# VALIDATE DATE RANGE
# ============================================================

if start_date > end_date:

    st.error(
        "Start date cannot be greater than end date."
    )

    st.stop()


# ============================================================
# FILTER EMOTIONAL DATA
# ============================================================

filtered_emotional = emotional_history[
    (
        emotional_history["timestamp"].dt.date
        >= start_date
    )
    &
    (
        emotional_history["timestamp"].dt.date
        <= end_date
    )
].copy()


# ============================================================
# DISPLAY SELECTED DATA
# ============================================================

st.subheader("📌 Selected Report Period")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Emotional Records",
        len(filtered_emotional)
    )

with col2:

    if not filtered_emotional.empty:
        dominant_emotion = (
            filtered_emotional["emotion"]
            .value_counts()
            .idxmax()
        )
    else:
        dominant_emotion = "No data"

    st.metric(
        "Most Frequent Emotion",
        dominant_emotion
    )

with col3:

    if not filtered_emotional.empty:
        avg_confidence = (
            filtered_emotional["confidence"]
            .mean()
        )
    else:
        avg_confidence = 0

    st.metric(
        "Average Confidence",
        f"{avg_confidence:.2f}%"
    )


# ============================================================
# TREND DATA
# ============================================================

st.subheader("📈 Emotional Trends")

if not filtered_emotional.empty:

    daily_trends = (
        filtered_emotional
        .set_index("timestamp")
        .resample("D")
        .agg(
            Records=("id", "count"),
            Average_Confidence=("confidence", "mean")
        )
        .reset_index()
    )

    st.dataframe(
        daily_trends,
        use_container_width=True
    )

else:

    st.info(
        "No emotional records found for the selected dates."
    )


# ============================================================
# EMOTIONAL ANALYSIS TABLE
# ============================================================

st.subheader("🧠 Emotional Analysis")

st.dataframe(
    filtered_emotional,
    use_container_width=True
)


# ============================================================
# RECOMMENDATIONS
# ============================================================

st.subheader("💡 Recommendations and Feedback")

st.dataframe(
    feedback_data,
    use_container_width=True
)


# ============================================================
# CREATE REPORT DATA
# ============================================================

st.subheader("📥 Download Reports")

csv_report = create_csv_report(
    filtered_emotional,
    feedback_data
)

pdf_report = create_pdf_report(
    filtered_emotional,
    feedback_data
)


# ============================================================
# DOWNLOAD BUTTONS
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.download_button(
        label="📄 Download CSV/Excel Report",
        data=csv_report,
        file_name="moodmentor_report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )


with col2:

    st.download_button(
        label="📕 Download PDF Report",
        data=pdf_report,
        file_name="moodmentor_report.pdf",
        mime="application/pdf"
    )


st.success(
    "Reports are generated dynamically from the selected "
    "date range and database records."
)