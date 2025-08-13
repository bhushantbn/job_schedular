import os
import json
import smtplib
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random

# Load environment variables
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

HISTORY_FILE = "last_questions.json"
MAX_HISTORY = 100  # Keep last 100 questions only


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_history(history):
    # Keep only last MAX_HISTORY entries
    history = history[-MAX_HISTORY:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def generate_unique_questions(history):
    history_questions = {q["question"] for q in history}
    unique_qas = []

    while len(unique_qas) < 10:
        prompt = (
            "Generate one unique senior-level software testing interview question "
            "with its answer for a Senior Quality Analyst with 10 years experience "
            "(manual + automation, ecommerce). Return in JSON: {question: '', answer: ''}."
        )

        try:
            response = model.generate_content(prompt)
            qa_text = response.text.strip()

            qa = json.loads(qa_text)  # Expecting JSON output from Gemini

            if qa["question"] not in history_questions:
                unique_qas.append(qa)
                history_questions.add(qa["question"])
        except Exception as e:
            print("Error generating question:", e)

    return unique_qas


def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)


def main():
    history = load_history()
    new_qas = generate_unique_questions(history)

    # Save updated history
    save_history(history + new_qas)

    # Prepare email body
    body = "\n\n".join(
        [f"Q: {qa['question']}\nA: {qa['answer']}" for qa in new_qas]
    )

    send_email(
        subject="Daily Senior QA Interview Questions",
        body=body
    )
    print("Email sent with 10 unique interview questions!")


if __name__ == "__main__":
    main()
