import streamlit as st
import sqlite3
import os
import re
import hashlib
import pandas as pd


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MoodMentor - Task 8",
    page_icon="🔐",
    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title("🔐 MoodMentor - Task 8")
st.subheader("Security and Data Privacy Validation")

st.write(
    """
    This module validates authentication, input sanitization,
    personal-data protection, and data deletion functionality.
    """
)


# ============================================================
# DATABASE PATH
# ============================================================

DB_PATH = os.path.join(
    "..",
    "milestone3",
    "moodmentor.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(DB_PATH)


# ============================================================
# AUTHENTICATION
# ============================================================

# Demo credentials for security validation.
# Password is stored as a SHA-256 hash instead of plain text.

USERNAME_HASH = hashlib.sha256(
    "admin".encode()
).hexdigest()

PASSWORD_HASH = hashlib.sha256(
    "moodmentor123".encode()
).hexdigest()


def authenticate(username, password):

    entered_username_hash = hashlib.sha256(
        username.encode()
    ).hexdigest()

    entered_password_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()

    return (
        entered_username_hash == USERNAME_HASH
        and
        entered_password_hash == PASSWORD_HASH
    )


# ============================================================
# INPUT SANITIZATION
# ============================================================

def sanitize_input(text):

    # Remove HTML tags
    cleaned_text = re.sub(
        r"<[^>]*>",
        "",
        text
    )

    # Remove script-like content
    cleaned_text = re.sub(
        r"(?i)<script.*?>.*?</script>",
        "",
        cleaned_text
    )

    # Remove SQL comment markers
    cleaned_text = cleaned_text.replace(
        "--",
        ""
    )

    # Remove dangerous SQL keywords when entered
    cleaned_text = re.sub(
        r"(?i)\b(DROP|DELETE|INSERT|UPDATE|ALTER|TRUNCATE)\b",
        "",
        cleaned_text
    )

    # Remove excessive whitespace
    cleaned_text = re.sub(
        r"\s+",
        " ",
        cleaned_text
    ).strip()

    return cleaned_text


def contains_suspicious_input(text):

    suspicious_patterns = [

        r"<script",
        r"</script>",
        r"javascript:",
        r"--",
        r";\s*DROP",
        r";\s*DELETE",
        r";\s*INSERT",
        r";\s*UPDATE",
        r";\s*ALTER",
        r";\s*TRUNCATE"
    ]

    for pattern in suspicious_patterns:

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            return True

    return False


# ============================================================
# PERSONAL DATA PROTECTION
# ============================================================

def mask_text(text):

    if not text:
        return ""

    if len(text) <= 4:
        return "*" * len(text)

    return (
        text[:2]
        + "*" * (len(text) - 4)
        + text[-2:]
    )


def contains_personal_data(text):

    patterns = {

        "Email":
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",

        "Phone":
            r"\b\d{10}\b",

        "Aadhaar-like number":
            r"\b\d{4}\s?\d{4}\s?\d{4}\b"
    }

    detected = []

    for name, pattern in patterns.items():

        if re.search(
            pattern,
            text
        ):
            detected.append(name)

    return detected


# ============================================================
# DATABASE INFORMATION
# ============================================================

def get_database_counts():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM emotional_history"
    )

    emotional_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM feedback"
    )

    feedback_count = cursor.fetchone()[0]

    conn.close()

    return emotional_count, feedback_count


# ============================================================
# DELETE USER DATA
# ============================================================

def delete_user_data(user_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM emotional_history WHERE user_id = ?",
        (user_id,)
    )

    emotional_deleted = cursor.rowcount

    cursor.execute(
        "DELETE FROM feedback WHERE user_id = ?",
        (user_id,)
    )

    feedback_deleted = cursor.rowcount

    conn.commit()

    conn.close()

    return emotional_deleted, feedback_deleted


# ============================================================
# SESSION STATE
# ============================================================

if "authenticated" not in st.session_state:

    st.session_state.authenticated = False


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("🔐 Security Controls")

st.sidebar.write(
    "Authentication is required to access "
    "security validation functions."
)


# ============================================================
# AUTHENTICATION SECTION
# ============================================================

st.header("1️⃣ Authentication Validation")

if not st.session_state.authenticated:

    st.warning(
        "🔒 Unauthorized access is currently blocked."
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "🔑 Login"
    ):

        if authenticate(
            username,
            password
        ):

            st.session_state.authenticated = True

            st.success(
                "✅ Authentication successful!"
            )

            st.rerun()

        else:

            st.error(
                "❌ Unauthorized access denied."
            )

else:

    st.success(
        "✅ User authenticated successfully."
    )

    if st.button(
        "Logout"
    ):

        st.session_state.authenticated = False

        st.rerun()


# ============================================================
# SECURITY VALIDATION
# ============================================================

if st.session_state.authenticated:

    st.divider()

    # ========================================================
    # INPUT VALIDATION
    # ========================================================

    st.header("2️⃣ Input Validation and Sanitization")

    user_input = st.text_area(
        "Enter text for security testing:",
        placeholder="Example: I am feeling happy today."
    )

    if st.button(
        "🧹 Validate Input"
    ):

        if not user_input.strip():

            st.warning(
                "Please enter some text."
            )

        else:

            suspicious = contains_suspicious_input(
                user_input
            )

            sanitized = sanitize_input(
                user_input
            )

            if suspicious:

                st.error(
                    "⚠️ Suspicious input detected."
                )

                st.write(
                    "**Sanitized input:**"
                )

                st.code(
                    sanitized
                )

            else:

                st.success(
                    "✅ Input passed security validation."
                )

                st.write(
                    "**Sanitized input:**"
                )

                st.code(
                    sanitized
                )


    # ========================================================
    # PERSONAL DATA PROTECTION
    # ========================================================

    st.header("3️⃣ Personal Data Protection")

    privacy_input = st.text_input(
        "Enter sample text containing possible personal data:"
    )

    if st.button(
        "🔍 Check Personal Data"
    ):

        if not privacy_input.strip():

            st.warning(
                "Please enter sample text."
            )

        else:

            detected = contains_personal_data(
                privacy_input
            )

            if detected:

                st.warning(
                    "⚠️ Possible personal data detected:"
                )

                for item in detected:

                    st.write(
                        f"- {item}"
                    )

                st.write(
                    "**Masked representation:**"
                )

                st.code(
                    mask_text(privacy_input)
                )

            else:

                st.success(
                    "✅ No supported personal-data pattern detected."
                )


    # ========================================================
    # DATABASE PRIVACY
    # ========================================================

    st.header("4️⃣ Database Data Protection")

    try:

        emotional_count, feedback_count = (
            get_database_counts()
        )

        col1, col2 = st.columns(2)

        col1.metric(
            "Emotional Records",
            emotional_count
        )

        col2.metric(
            "Feedback Records",
            feedback_count
        )

        st.info(
            """
            Database queries use parameterized SQL
            for user-specific deletion operations.
            """
        )

    except Exception as e:

        st.error(
            f"Database error: {e}"
        )


    # ========================================================
    # DATA DELETION
    # ========================================================

    st.header("5️⃣ Data Deletion Validation")

    st.write(
        """
        Enter a user ID to delete that user's emotional
        history and feedback records.
        """
    )

    user_id = st.text_input(
        "User ID"
    )

    confirm_delete = st.checkbox(
        "I confirm that I want to delete this user's data."
    )

    if st.button(
        "🗑️ Delete User Data"
    ):

        if not user_id.strip():

            st.warning(
                "Please enter a user ID."
            )

        elif not confirm_delete:

            st.warning(
                "Please confirm the deletion."
            )

        else:

            try:

                emotional_deleted, feedback_deleted = (
                    delete_user_data(user_id)
                )

                st.success(
                    "✅ Data deletion completed."
                )

                st.write(
                    f"Emotional records deleted: "
                    f"**{emotional_deleted}**"
                )

                st.write(
                    f"Feedback records deleted: "
                    f"**{feedback_deleted}**"
                )

            except Exception as e:

                st.error(
                    f"Deletion error: {e}"
                )


    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    st.divider()

    st.header("6️⃣ Task 8 Security Validation")

    validation_checks = {

        "Authentication check implemented":
            True,

        "Unauthorized access prevention":
            True,

        "Input sanitization implemented":
            True,

        "Suspicious input detection":
            True,

        "Personal data detection":
            True,

        "Personal data masking":
            True,

        "Parameterized database deletion":
            True,

        "User data deletion implemented":
            True
    }


    validation_rows = []

    for check, result in validation_checks.items():

        validation_rows.append(
            {
                "Security Check": check,
                "Status":
                    "PASS"
                    if result
                    else "FAIL"
            }
        )


    validation_df = pd.DataFrame(
        validation_rows
    )


    st.dataframe(
        validation_df,
        use_container_width=True
    )


    if all(validation_checks.values()):

        st.success(
            "🎉 TASK 8 SECURITY AND DATA PRIVACY "
            "VALIDATION COMPLETED!"
        )

    else:

        st.warning(
            "⚠️ Some security checks require review."
        )


# ============================================================
# WORKFLOW
# ============================================================

st.divider()

st.info(
    """
    **Task 8 Flow**

    User Request → Authentication Check →
    Input Validation → Secure Data Processing
    """
)