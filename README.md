# Daily Senior Quality Analyst Job Search (Ahmedabad)

This project automates the process of searching for **Senior Quality Analyst** jobs at top companies in **Ahmedabad** and sends the results to your email daily at **12 noon IST** using GitHub Actions.

---

## 📌 Features
- Automatically runs every day at 12 noon IST.
- Searches for latest job postings using RapidAPI.
- Sends results directly to your email.
- Fully serverless — runs on GitHub Actions (no need to keep PC on).

---

## 🛠️ Requirements
- Python 3.9+ (GitHub Actions uses latest Python by default)
- A **Gmail account** (with an App Password for SMTP)
- A **RapidAPI key** for job search

---

## 📂 Project Structure
.
├── job_search.py # Main Python script
├── requirements.txt # Python dependencies
├── .github/
│ └── workflows/
│ └── job_search.yml # GitHub Actions workflow file
└── README.md # Project documentation

------------------------------------------------

## ⚙️ Setup

### 1. Fork or Clone the Repository
```bash
git clone https://github.com/your-username/daily-job-search.git
cd daily-job-search
```
## 2. Install Dependencies (for local testing)

``` pip install -r requirements.txt ```

### 3. Create .env File (Optional for Local Run)



