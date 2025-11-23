# Detailed Deployment and Local Run Instructions

This document provides the exact steps required to set up the Python environment and run the Student Introduction Scorer application locally.

## Prerequisites

Before starting, ensure you have the following software installed on your system:

1. **Python 3.8+**: The project is built on Python.
2. **Java Runtime Environment (JRE) 8+**: The `language-tool-python` library, which is used for grammar and language checks, requires a working Java installation to run its internal server.

---

## Step 1: Clone the Repository

Clone the project from your public GitHub repository to your local machine:

```bash
git clone https://github.com/yatharthkukadia/nirmaan_ai_case_study.git
cd nirmaan_ai_case_study
```

---

## Step 2: Create and Activate a Virtual Environment

Using a virtual environment is recommended to isolate dependencies.

### **For Windows (Command Prompt / PowerShell)**

```bash
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate
```

### **For macOS/Linux (Bash)**

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

---

## Step 3: Install Required Python Packages

Install all necessary dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

**Note:** The `sentence-transformers` package may take a few minutes to install and download its ML model.

---

## Step 4: Run the Streamlit Application

Start the web application:

```bash
streamlit run app.py
```

### Expected Access
The terminal will show URLs similar to:

- **Local URL:** `http://localhost:8501`
- **Network URL:** `http://[YOUR_IP]:8501`

Your default browser should automatically open the Local URL.

The application UI will load and will be ready to accept a transcript for scoring.

---

## Step 5: Deactivate the Virtual Environment

When done, exit the virtual environment:

```bash
deactivate
```

