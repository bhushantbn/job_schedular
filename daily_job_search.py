import requests
import smtplib
from email.mime.text import MIMEText
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Email Configuration
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# RapidAPI Configuration
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
RAPIDAPI_URL = os.getenv("RAPIDAPI_URL", "https://jsearch.p.rapidapi.com/search")

# Roles and Locations to search
ROLES = [
    "Senior Quality Analyst",
    "Senior QA Tester",
    "Senior Quality Engineer",
    "Senior QA Lead",
    "Magento QA Lead",
    "Commerce QA"
]
LOCATIONS = ["Ahmedabad","Remote"]

def search_jobs():
    all_jobs = []
    for role in ROLES:
        for location in LOCATIONS:
            print(f"Searching: {role} in {location}...")
            url = "https://jsearch.p.rapidapi.com/search"
            querystring = {"query": f"{role} in {location}, India", "page": "1", "num_pages": "1"}
            headers = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": RAPIDAPI_HOST}

            try:
                res = requests.get(url, headers=headers, params=querystring, timeout=10)
                data = res.json()
                jobs = data.get("data", [])
                if jobs:
                    for job in jobs:
                        all_jobs.append({
                            "title": job.get("job_title", "No Title"),
                            "company": job.get("employer_name", "Unknown Company"),
                            "location": location,
                            "link": job.get("job_apply_link", "#")
                        })
                else:
                    all_jobs.append({
                        "title": f"No jobs found for {role} in {location}",
                        "company": "-",
                        "location": location,
                        "link": "#"
                    })
            except Exception as e:
                all_jobs.append({
                    "title": f"Error searching {role} in {location}",
                    "company": str(e),
                    "location": location,
                    "link": "#"
                })

    send_email(all_jobs)

def send_email(jobs):
    date_today = datetime.datetime.now().strftime("%Y-%m-%d")
    html = f"""
    <html><body>
    <h2>QA Job Results – {date_today}</h2>
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color:#f2f2f2;">
            <th>Role</th><th>Company</th><th>Location</th><th>Apply Link</th>
        </tr>
    """
    for job in jobs:
        html += f"""
        <tr>
            <td>{job['title']}</td>
            <td>{job['company']}</td>
            <td>{job['location']}</td>
            <td><a href="{job['link']}">Apply Here</a></td>
        </tr>
        """
    html += "</table></body></html>"

    msg = MIMEText(html, "html")
    msg["Subject"] = f"QA Job Listings – {date_today}"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as ex:
        print(f"❌ Failed to send email: {ex}")

if __name__ == "__main__":
    search_jobs()
