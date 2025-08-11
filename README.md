# Python Automation Schedular

This repository contains a collection of Python scripts for various automation tasks, including daily job searches, interview question generation, and web browser interactions using Selenium.

---

## 📌 Features

- **Daily Job Search**: Automatically searches for jobs on RapidAPI based on a predefined list of roles and locations, and sends a summary email.
- **Daily Interview Questions**: Generates a set of interview questions and answers for a Senior QA role using the Gemini API and sends them to your email.
- **GitHub Actions Integration**: The job search and interview question scripts are configured to run on a schedule using GitHub Actions.

---

## 📂 Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── job_search.yml
├── daily_job_search.py
├── daily_interview_questions.py
├── requirements.txt
├── README.md
├── ... (other selenium scripts)
```

---

## ⚙️ Requirements

- Python 3.x
- A Gmail account (with an App Password for SMTP).
- A RapidAPI key for the job search script.
- A Google Gemini API key for the interview questions script.

---

## 🚀 Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/your_directory_name.git
cd Your Directory Name
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` File
Create a `.env` file in the root directory and add the following secrets:

```env
# For daily_job_search.py
RAPIDAPI_KEY=your_rapidapi_key
RAPIDAPI_HOST=jsearch.p.rapidapi.com
RAPIDAPI_URL=https://jsearch.p.rapidapi.com/search

# For daily_interview_questions.py
GEMINI_API_KEY=your_gemini_api_key

# For both scripts
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=your_email@gmail.com
```

---

## Usage

### Run Scripts Locally

To run the scripts locally, use the following commands:

```bash
# For daily job search
python daily_job_search.py

# For daily interview questions
python daily_interview_questions.py
```

### Run with GitHub Actions

The `daily_job_search.py` script is configured to run every 6 hours via GitHub Actions. To enable this, you need to add the following secrets to your GitHub repository settings:

- `EMAIL_SENDER`
- `EMAIL_PASSWORD`
- `EMAIL_RECEIVER`
- `RAPIDAPI_KEY`
- `RAPIDAPI_HOST`
- `RAPIDAPI_URL`
- `GEMINI_API_KEY`

You can also manually trigger the workflow from the "Actions" tab in your GitHub repository.

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---

## 📖 Acknowledgments

- [RapidAPI](https://rapidapi.com/)
- [Google Gemini](https://gemini.google.com/)