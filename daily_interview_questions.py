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
model = genai.GenerativeModel("gemini-1.5-flash")

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
    attempts = 0
    max_attempts = 5  # Number of API calls to make if needed

    while len(unique_qas) < 10 and attempts < max_attempts:
        attempts += 1
        num_to_generate = 10 - len(unique_qas) + 5  # Generate a few extra to account for potential duplicates
        prompt = f"""Generate {num_to_generate} unique senior-level software engineering interview questions with their answers. Ensure they are diverse and not duplicates of each other. Return ONLY valid JSON format: an array of objects like [{{"question": "your question here", "answer": "your answer here"}}, ...]"""

        try:
            response = model.generate_content(prompt)
            qa_text = response.text.strip()
            
            # Clean up response - remove markdown formatting if present
            if qa_text.startswith('```json'):
                qa_text = qa_text.replace('```json', '').strip()
            elif qa_text.startswith('```'):
                qa_text = qa_text.replace('```', '').strip()

            qa_list = json.loads(qa_text)  # Expecting JSON array from Gemini

            # Validate the list structure
            if isinstance(qa_list, list):
                for qa in qa_list:
                    if isinstance(qa, dict) and "question" in qa and "answer" in qa:
                        if qa["question"] not in history_questions and qa["question"] not in {u["question"] for u in unique_qas}:
                            unique_qas.append(qa)
                            history_questions.add(qa["question"])
                            print(f"Added unique question. Total: {len(unique_qas)}/10")
                            if len(unique_qas) >= 10:
                                break
                    else:
                        print("Invalid QA structure in list, skipping...")
            else:
                print("Response not a list, retrying...")
                
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {qa_text}")
        except Exception as e:
            print(f"Error generating questions: {e}")

    if len(unique_qas) < 10:
        print(f"Warning: Only generated {len(unique_qas)} questions, using fallback for remaining")
        # Fallback questions in case not enough generated
        fallback_qas = [
            {
                "question": "What is an API?",
                "answer": "An API (Application Programming Interface) acts as an interface that allows two software systems to communicate with each other."
            },
            {
                "question": "What are the key characteristics of a RESTful system?",
                "answer": "REST (Representational State Transfer) is an architectural style for designing networked applications. Key characteristics include a client-server model, statelessness, cacheability, a uniform interface, and a layered system."
            },
            {
                "question": "What are the differences between REST and SOAP?",
                "answer": "REST is generally more versatile and faster than SOAP, supporting various data formats like JSON and XML, while SOAP primarily uses XML. REST is often preferred for its simplicity and scalability."
            },
            {
                "question": "What are the common HTTP methods used in REST APIs?",
                "answer": "Commonly used HTTP methods include GET (retrieve), POST (create), PUT (update/replace), PATCH (partial update), and DELETE (remove)."
            },
            {
                "question": "What is the difference between PUT and POST?",
                "answer": "POST is used to create a new resource, while PUT is used to update an existing resource or create one if it doesn't exist."
            },
            {
                "question": "What is idempotency in the context of REST APIs?",
                "answer": "Idempotency means that making the same request multiple times will have the same effect as making it once. For example, a DELETE request is idempotent."
            },
            {
                "question": "How would you handle API versioning?",
                "answer": "Versioning is crucial for maintaining backward compatibility. Common strategies include including the version number in the URI (e.g., '/v1/users'), in a request header, or as a query parameter."
            },
            {
                "question": "How do you secure an API?",
                "answer": "Securing an API involves multiple layers, including implementing robust authentication and authorization, using HTTPS to encrypt data in transit, validating input to prevent attacks like SQL injection, and implementing rate limiting."
            },
            {
                "question": "What are common authentication methods for APIs?",
                "answer": "Common methods include API keys, OAuth 2.0 (often used for delegated access), and JSON Web Tokens (JWT) for token-based authentication."
            },
            {
                "question": "What is the purpose of an API Gateway?",
                "answer": "An API Gateway serves as a single entry point for all API requests, handling concerns like request routing, authentication, rate limiting, and logging."
            }
        ]
        # Add fallbacks until we reach 10, avoiding duplicates
        for fb in fallback_qas:
            if len(unique_qas) >= 10:
                break
            if fb["question"] not in history_questions and fb["question"] not in {u["question"] for u in unique_qas}:
                unique_qas.append(fb)
                history_questions.add(fb["question"])

    # Trim to exactly 10 if more
    return unique_qas[:10]


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
        body = "Daily Software Engineering Interview Questions\n" + "="*50 + "\n\n"
        body += "\n\n".join([
            f"Q{i+1}: {qa['question']}\n\nA{i+1}: {qa['answer']}" 
            for i, qa in enumerate(new_qas)
        ])
        body += f"\n\n" + "="*50
        body += f"\nTotal questions in history: {len(history) + len(new_qas)}"

        send_email(
            subject="Daily Software Engineering Interview Questions",
            body=body
        )
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error in main process: {e}")
        # Send error notification email
        try:
            send_email(
                subject="Daily SWE Questions - Error Occurred",
                body=f"An error occurred while generating daily questions:\n\n{str(e)}"
            )
        except:
            print("Failed to send error notification email")


if __name__ == "__main__":
    main()