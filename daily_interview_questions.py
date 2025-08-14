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

# Gemini setup - UPDATED MODEL NAME
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

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
    max_attempts = 20  # Prevent infinite loop

    while len(unique_qas) < 10 and max_attempts > 0:
        prompt = (
            "Generate one unique senior-level software testing interview question "
            "with its answer for a Senior Quality Analyst with 10 years experience "
            "(manual + automation, ecommerce). Return ONLY valid JSON format: "
            '{"question": "your question here", "answer": "your answer here"}'
        )

        try:
            response = model.generate_content(prompt)
            qa_text = response.text.strip()
            
            # Clean up response - remove markdown formatting if present
            if qa_text.startswith('```json'):
                qa_text = qa_text.replace('```json', '').replace('```', '').strip()
            elif qa_text.startswith('```'):
                qa_text = qa_text.replace('```', '').strip()

            qa = json.loads(qa_text)  # Expecting JSON output from Gemini

            # Validate the JSON structure
            if isinstance(qa, dict) and "question" in qa and "answer" in qa:
                if qa["question"] not in history_questions:
                    unique_qas.append(qa)
                    history_questions.add(qa["question"])
                    print(f"Generated question {len(unique_qas)}/10")
                else:
                    print("Duplicate question, retrying...")
            else:
                print("Invalid JSON structure, retrying...")
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {qa_text}")
        except Exception as e:
            print(f"Error generating question: {e}")
        
        max_attempts -= 1

    if len(unique_qas) == 0:
        print("Warning: No questions generated, using fallback")
        # Fallback question in case all attempts fail
        unique_qas = [{
            "question": "Describe your approach to testing an e-commerce checkout process for both functional and non-functional requirements.",
            "answer": "I would create a comprehensive test plan covering functional tests (payment processing, inventory updates, order confirmation), usability tests (user journey, accessibility), performance tests (load testing during peak times), security tests (payment data protection, SQL injection), and integration tests (third-party payment gateways, inventory systems)."
        }]

    return unique_qas


def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def main():
    try:
        history = load_history()
        print(f"Loaded {len(history)} questions from history")
        
        new_qas = generate_unique_questions(history)
        print(f"Generated {len(new_qas)} new questions")

        # Save updated history
        save_history(history + new_qas)

        # Prepare email body
        body = "Daily Senior QA Interview Questions\n" + "="*50 + "\n\n"
        body += "\n\n".join([
            f"Q{i+1}: {qa['question']}\n\nA{i+1}: {qa['answer']}" 
            for i, qa in enumerate(new_qas)
        ])
        body += f"\n\n" + "="*50
        body += f"\nTotal questions in history: {len(history) + len(new_qas)}"

        send_email(
            subject="Daily Senior QA Interview Questions",
            body=body
        )
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error in main process: {e}")
        # Send error notification email
        try:
            send_email(
                subject="Daily QA Questions - Error Occurred",
                body=f"An error occurred while generating daily questions:\n\n{str(e)}"
            )
        except:
            print("Failed to send error notification email")


if __name__ == "__main__":
    main()