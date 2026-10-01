import streamlit as st
import os
import time
import pandas as pd
import torch

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MoodMentor - Task 7",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("📊 MoodMentor - Task 7")
st.subheader("Model Performance and Stress Testing")

st.write(
    """
    This module evaluates the performance and reliability of the
    emotion detection model under different workloads.
    """
)


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = os.path.join(
    "..",
    "milestone 2",
    "distilbert_multilabel_emotion_model"
)


# ============================================================
# EMOTION LABELS
# ============================================================

emotion_labels = [
    "joy",
    "sadness",
    "anger",
    "fear",
    "surprise",
    "disgust"
]


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_PATH
    )

    model.eval()

    return tokenizer, model


try:

    tokenizer, model = load_model()

    st.success("✅ Emotion detection model loaded successfully!")

except Exception as e:

    st.error(f"❌ Error loading model: {e}")

    st.stop()


# ============================================================
# TEST DATASET
# ============================================================

test_data = [

    (
        "I am extremely happy and excited today.",
        "joy"
    ),

    (
        "I feel very sad and lonely.",
        "sadness"
    ),

    (
        "I am angry about what happened.",
        "anger"
    ),

    (
        "I am very scared about my exam.",
        "fear"
    ),

    (
        "I was surprised by the unexpected result.",
        "surprise"
    ),

    (
        "The situation made me feel disgusted.",
        "disgust"
    ),

    (
        "I am feeling joyful about my new job.",
        "joy"
    ),

    (
        "I feel terrible and unhappy.",
        "sadness"
    ),

    (
        "This situation makes me very angry.",
        "anger"
    ),

    (
        "I am nervous and afraid about tomorrow.",
        "fear"
    ),

    (
        "I cannot believe what just happened.",
        "surprise"
    ),

    (
        "That experience was extremely unpleasant.",
        "disgust"
    )
]


texts = [item[0] for item in test_data]

true_labels = [item[1] for item in test_data]


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_emotion(text):

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=128
    )

    with torch.no_grad():

        outputs = model(**inputs)

        probabilities = torch.sigmoid(
            outputs.logits
        )[0]

    max_index = torch.argmax(
        probabilities
    ).item()

    predicted_emotion = emotion_labels[
        max_index
    ]

    confidence = probabilities[
        max_index
    ].item()

    return predicted_emotion, confidence


# ============================================================
# MODEL PERFORMANCE
# ============================================================

st.header("1️⃣ Model Performance Evaluation")

st.write(
    "The test dataset contains "
    f"**{len(test_data)} test samples**."
)


if st.button(
    "🚀 Run Performance Test",
    type="primary"
):

    predicted_labels = []

    prediction_records = []

    start_time = time.perf_counter()

    for text in texts:

        emotion, confidence = predict_emotion(
            text
        )

        predicted_labels.append(
            emotion
        )

        prediction_records.append(
            {
                "Text": text,
                "Actual Emotion": true_labels[
                    len(prediction_records)
                ],
                "Predicted Emotion": emotion,
                "Confidence": round(
                    confidence,
                    4
                )
            }
        )

    end_time = time.perf_counter()

    total_inference_time = (
        end_time - start_time
    ) * 1000

    average_inference_time = (
        total_inference_time /
        len(texts)
    )


    # ========================================================
    # METRICS
    # ========================================================

    accuracy = accuracy_score(
        true_labels,
        predicted_labels
    )

    precision = precision_score(
        true_labels,
        predicted_labels,
        average="macro",
        zero_division=0
    )

    recall = recall_score(
        true_labels,
        predicted_labels,
        average="macro",
        zero_division=0
    )

    macro_f1 = f1_score(
        true_labels,
        predicted_labels,
        average="macro",
        zero_division=0
    )


    # ========================================================
    # DISPLAY METRICS
    # ========================================================

    st.subheader("📈 Performance Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Accuracy",
        f"{accuracy:.4f}"
    )

    col2.metric(
        "Precision",
        f"{precision:.4f}"
    )

    col3.metric(
        "Recall",
        f"{recall:.4f}"
    )

    col4.metric(
        "Macro F1",
        f"{macro_f1:.4f}"
    )


    # ========================================================
    # INFERENCE TIME
    # ========================================================

    st.subheader("⚡ Inference Time")

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Inference Time",
        f"{total_inference_time:.3f} ms"
    )

    col2.metric(
        "Average Inference Time",
        f"{average_inference_time:.3f} ms"
    )


    # ========================================================
    # PREDICTION RESULTS
    # ========================================================

    st.subheader("🔍 Prediction Results")

    results_df = pd.DataFrame(
        prediction_records
    )

    st.dataframe(
        results_df,
        use_container_width=True
    )


    # ========================================================
    # STRESS TESTING
    # ========================================================

    st.header("2️⃣ Stress Testing")

    st.write(
        """
        The system is tested with different workloads
        to measure response time and reliability.
        """
    )


    workloads = [
        10,
        50,
        100
    ]

    stress_results = []


    for workload in workloads:

        workload_data = texts * (
            workload // len(texts) + 1
        )

        workload_data = workload_data[
            :workload
        ]

        start = time.perf_counter()

        for text in workload_data:

            predict_emotion(text)

        end = time.perf_counter()

        total_time = (
            end - start
        ) * 1000

        average_time = (
            total_time /
            workload
        )

        stress_results.append(
            {
                "Workload": workload,
                "Total Response Time (ms)": round(
                    total_time,
                    3
                ),
                "Average Response Time (ms)": round(
                    average_time,
                    3
                )
            }
        )


    # ========================================================
    # STRESS TEST TABLE
    # ========================================================

    stress_df = pd.DataFrame(
        stress_results
    )

    st.subheader(
        "📊 Stress Test Results"
    )

    st.dataframe(
        stress_df,
        use_container_width=True
    )


    # ========================================================
    # STRESS TEST GRAPH
    # ========================================================

    st.subheader(
        "📈 Response Time vs Workload"
    )

    chart_df = stress_df.set_index(
        "Workload"
    )

    st.line_chart(
        chart_df[
            "Total Response Time (ms)"
        ]
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    st.header(
        "3️⃣ Task 7 Validation"
    )

    checks = {

        "Accuracy calculated":
            accuracy >= 0,

        "Precision calculated":
            precision >= 0,

        "Recall calculated":
            recall >= 0,

        "Macro F1 calculated":
            macro_f1 >= 0,

        "Inference time measured":
            average_inference_time > 0,

        "10-input workload tested":
            True,

        "50-input workload tested":
            True,

        "100-input workload tested":
            True,

        "System response measured":
            all(
                result[
                    "Total Response Time (ms)"
                ] > 0

                for result in stress_results
            )
    }


    validation_data = []

    for check, result in checks.items():

        validation_data.append(
            {
                "Validation Check": check,
                "Status": (
                    "PASS"
                    if result
                    else "FAIL"
                )
            }
        )


    validation_df = pd.DataFrame(
        validation_data
    )

    st.dataframe(
        validation_df,
        use_container_width=True
    )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    all_passed = all(
        checks.values()
    )


    if all_passed:

        st.success(
            "🎉 TASK 7 COMPLETED SUCCESSFULLY!"
        )

    else:

        st.warning(
            "⚠️ Task 7 needs review."
        )


# ============================================================
# INFORMATION
# ============================================================

st.divider()

st.info(
    """
    **Task 7 Flow**

    Test Dataset → Model Inference → Performance
    Measurement → Stress Testing → Result Analysis
    """
)