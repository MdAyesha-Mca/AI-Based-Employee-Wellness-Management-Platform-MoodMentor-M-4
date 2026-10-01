# MoodMentor

## AI-Based Employee Wellness Management Platform

MoodMentor is an AI-based employee wellness platform that analyzes emotional states from user-provided text and provides personalized wellness recommendations.

The project combines Natural Language Processing, emotion classification, recommendation systems, emotional trend tracking, feedback learning, SQLite database storage, and a Streamlit-based user interface.


## Project Objectives

The main objectives of MoodMentor are:

- Analyze user-provided emotional text.
- Detect emotions such as joy, sadness, anger, fear, surprise, and disgust.
- Estimate emotion intensity and emotional state.
- Analyze sentiment and emotional trends.
- Generate personalized wellness recommendations.
- Rank recommendations according to user context.
- Store emotional history and recommendation feedback.
- Provide an interactive Streamlit dashboard.
- Provide a reusable Python package and command-line interface.
- Validate model performance, security, and data privacy.


## Technologies Used

- Python
- Streamlit
- Natural Language Processing (NLP)
- NLTK
- Transformers
- PyTorch
- Scikit-learn
- Pandas
- NumPy
- SQLite
- ReportLab
- OpenPyXL
- Setuptools
- argparse


## System Requirements

- Python 3.10 or later
- Windows, Linux, or macOS
- VS Code or any Python-compatible IDE
- Internet connection for installing required packages and downloading model resources
- Sufficient storage for the trained emotion models and project datasets

## Installation and Setup

### 1. Open the project folder

Navigate to the Milestone 4 directory:

```powershell
cd "C:\Users\mdsam\OneDrive\Desktop\project infosys\milestone 4"

### 2. Install the MoodMentor package

Run:

```powershell
python -m pip install .

## Running the Streamlit Application

MoodMentor provides a Streamlit-based interface for interactive use and demonstration.

Navigate to the Milestone 4 folder:

```powershell
cd "C:\Users\mdsam\OneDrive\Desktop\project infosys\milestone 4"



## Emotion Analysis Model

MoodMentor uses a transformer-based emotion classification model for detecting emotional states from user text.

The supported emotion categories are:

- Joy
- Sadness
- Anger
- Fear
- Surprise
- Disgust

The emotion analysis module provides:

- Dominant emotion
- Confidence score
- Emotion intensity
- Sentiment polarity
- Emotional severity
- Mixed emotional state
- Multiple detected emotions

The trained model is stored in the Milestone 2 directory and is used by the Milestone 3 and Milestone 4 application components.


## Recommendation System

MoodMentor generates personalized wellness recommendations based on the user's emotional state and contextual information.

The recommendation pipeline includes:

1. Emotion detection
2. Emotion intensity analysis
3. Personalized recommendation
4. Hybrid recommendation
5. Semantic wellness-content matching
6. Recommendation ranking
7. Recommendation explainability
8. Feedback-based learning

The recommendation system uses information such as:

- Detected emotion
- Emotion intensity
- Wellness preference
- Previous interaction
- Recommendation history
- Emotional trend

Example wellness recommendations include:

- Guided breathing exercises
- Meditation
- Relaxation activities
- Positive wellness activities



## Database and Feedback

MoodMentor uses SQLite for storing application data.

The main database file is:

```text
moodmentor.db



## Security and Data Privacy

MoodMentor includes security and data privacy validation to help protect application data.

Security measures include:

- User authentication
- Input sanitization
- Detection and masking of sensitive information
- Parameterized SQL queries
- User-specific database operations
- Database security validation

The application was tested to verify that user input and database operations are handled safely.

Sensitive information should not be entered into the application unless required for testing.



## Testing and Validation

MoodMentor was tested across the major application components.

The validation included:

- Streamlit application startup testing
- Emotion analysis testing
- Emotion intensity testing
- Sentiment analysis testing
- Personalized recommendation testing
- Recommendation ranking testing
- Emotional history testing
- Recommendation feedback testing
- Empty-input error handling
- Model performance testing
- Stress testing
- Security and data privacy validation
- Package installation testing
- CLI version testing
- CLI analysis testing
- Clean-environment installation testing

### Final Application Test

A sample emotional input was processed successfully through the Streamlit application.

The application successfully displayed:

- Preprocessed text
- Dominant emotion
- Confidence score
- Emotion intensity
- Sentiment
- Personalized wellness recommendation
- Recommendation ranking
- Related wellness content
- Emotional history
- Recommendation feedback

Empty input was also tested and the application correctly displayed an input validation message.




## Deployment Preparation

Before deployment, verify the following requirements:

1. Python 3.10 or later is installed.
2. All required project files are available.
3. Trained emotion models are available.
4. Required datasets are available.
5. The SQLite database is accessible.
6. Required Python packages are installed.
7. The Streamlit application starts successfully.
8. The main application workflow is tested.
9. Error handling is verified.
10. Security and data privacy validation is completed.

### Run the Application

Navigate to the Milestone 4 directory:

```powershell
cd "C:\Users\mdsam\OneDrive\Desktop\project infosys\milestone 4"



## Command-Line Usage

MoodMentor provides a command-line interface for basic application interaction.

### Check Version

Run:

```powershell
python -m moodmentor.cli --version


### Analyze Text

Run:

```powershell
python -m moodmentor.cli --analyze "I am feeling happy today"



## Final Project Deliverables

The final MoodMentor project deliverables include:

- Source code for Milestone 1 to Milestone 4
- Trained emotion classification models
- Project datasets
- SQLite database
- Streamlit applications
- Personalized recommendation modules
- Recommendation ranking and validation modules
- Emotional trend tracking
- Recommendation history and feedback
- Search and filtering functionality
- Report generation and export
- Model performance and stress testing
- Security and data privacy validation
- Python package configuration
- Command-line interface
- Project documentation

## Project Handover

The project is prepared for demonstration and final review.

The documentation provides information about:

- Project objectives
- Technologies used
- Installation and setup
- Streamlit application usage
- CLI usage
- Emotion analysis model
- Recommendation system
- Database and feedback
- Security and data privacy
- Testing and validation
- Deployment preparation
- Final project deliverables

## Conclusion

MoodMentor integrates artificial intelligence, natural language processing, emotion analysis, personalized recommendations, emotional history, feedback, visualization, reporting, security validation, and packaging into an employee wellness platform.

The application has been tested through functional testing, model validation, security validation, package installation, CLI testing, clean-environment testing, and final Streamlit application testing.

The project is ready for final demonstration, review, and handover.