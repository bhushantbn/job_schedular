import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import os

# Email config
EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD =os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Mock Gemini API call - replace with actual Google Gemini API call
def generate_qa_from_gemini():
    # Prompt to generate 10 QA pairs for senior QA role
    prompt = (
        "Generate 10 interview questions and detailed answers for a Senior Quality Analyst "
        "with 10 years of experience in manual and automation testing. Format the output clearly "
        "with Q1:, A1:, Q2:, A2:, etc."
    )
    
    # MOCKED response (replace with your actual Gemini API interaction)
    mocked_response = """
Q1: What is your approach to designing test cases?
A1: I analyze requirements thoroughly and create test cases that cover positive, negative, boundary, and edge cases to ensure comprehensive coverage.

Q2: How do you handle flaky tests in your automation suite?
A2: I identify flaky tests using logs and reruns, then stabilize them by improving waits, fixing timing issues, or isolating environment problems.

Q3: Explain the benefits of BDD in test automation.
A3: BDD promotes collaboration among business, development, and QA teams, resulting in shared understanding and more maintainable automated tests.

Q4: What tools have you used for automation testing?
A4: I've worked extensively with Selenium, Playwright, TestNG, and Jenkins for continuous integration.

Q5: How do you manage regression testing in tight deadlines?
A5: Prioritize critical test cases, automate as many as possible, and use risk-based testing to focus on high-impact areas.

Q6: Describe your experience with API testing.
A6: I use Postman and REST-assured to create and automate API tests, validating responses and performance.

Q7: How do you ensure quality in Agile environments?
A7: By participating in sprint planning, continuous testing, and frequent communication with developers and product owners.

Q8: What metrics do you track for testing effectiveness?
A8: Defect density, test coverage, automation pass rate, and test execution time.

Q9: How do you mentor junior testers?
A9: Through knowledge sharing sessions, pair testing, and reviewing their test cases and scripts.

Q10: Explain your experience integrating automation into CI/CD pipelines.
A10: I configure Jenkins pipelines to trigger automated tests on code check-ins, ensuring quick feedback on quality.
"""
    return mocked_response.strip()

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    qa_content = generate_qa_from_gemini()
    email_subject = f"Daily Senior QA Interview Questions and Answers - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(email_subject, qa_content)
    print("Email sent with generated questions and answers!")

if __name__ == "__main__":
    main()
