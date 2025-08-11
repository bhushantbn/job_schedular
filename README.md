# Daily Job Search By Location

This project automates the process of searching for **Senior Quality Analyst** jobs at top companies in **Location** and sends the results to your email daily using GitHub Actions.

---

## 📌 Features
- Automatically runs every day at scheduled intervals.
- Searches for the latest job postings using RapidAPI.
- Sends results directly to your email.
- Fully serverless — runs on GitHub Actions (no need to keep PC on).

---

## 🛠️ Requirements
- Python 3.9+ (GitHub Actions uses the latest Python by default).
- A **Gmail account** (with an App Password for SMTP).
- A **RapidAPI key** for job search.

---

## 📂 Project Structure
```text
.
├── daily_job_search.py     # Main Python script for job search automation
├── requirements.txt        # Python dependencies
├── .github/
│   └── workflows/
│       └── daily_job_search.yml  # GitHub Actions workflow file
└── README.md               # Project documentation
```

---

## ⚙️ Setup

### 1. Fork or Clone the Repository
```bash
git clone https://github.com/your-username/daily-job-search.git
cd daily-job-search
```

### 2. Install Dependencies (for local testing)
```bash
pip install -r requirements.txt
```

### 3. Create `.env` File (Optional for Local Run)
Create a `.env` file in the root directory and add the following:
```env
RAPIDAPI_KEY=your_rapidapi_key
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

---

## 🚀 Usage

### Run Locally
To test the script locally, execute:
```bash
python daily_job_search.py
```

### Run on GitHub Actions
The script is configured to run automatically using the `daily_job_search.yml` workflow file. Ensure you set the required secrets in your GitHub repository:
- `RAPIDAPI_KEY`
- `SMTP_EMAIL`
- `SMTP_PASSWORD`

---

## 🤝 Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.

---

## 📜 License
This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## 📖 Acknowledgments
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [RapidAPI](https://rapidapi.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)



