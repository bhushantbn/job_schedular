import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from dotenv import load_dotenv
import os
import google.generativeai as genai
import random

# Load environment variables
load_dotenv()

EMAIL_SENDER = os.getenv('EMAIL_SENDER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_RECEIVER = os.getenv('EMAIL_RECEIVER')
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

def generate_qa_from_gemini():
    prompt = (
        "Generate 10 UNIQUE and DIFFERENT interview questions and detailed answers "
        "for a Senior Quality Analyst with 10 years of experience in manual and automation testing. "
        "Avoid repeating previous questions. Make them practical and scenario-based. "
        "Format as Q1:, A1:, Q2:, A2:, etc."
    )

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def main():
    qa_content = generate_qa_from_gemini()
    email_subject = f"Daily Senior QA Interview Q&A - {datetime.now().strftime('%Y-%m-%d')}"
    send_email(email_subject, qa_content)
    print("✅ Email sent with fresh interview questions!")

if __name__ == "__main__":
    main()
