import os
import json
import smtplib
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import datetime
import hashlib

# Load environment variables
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini setup - UPDATED MODEL NAME
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

HISTORY_FILE = "last_questions.json"
MAX_HISTORY = 200  # Increased history size to better track uniqueness

topics = [
    "automation frameworks in e-commerce",
    "Selenium WebDriver advanced techniques",
    "API testing for e-commerce backends",
    "performance testing under high load",
    "security vulnerability assessment",
    "accessibility compliance (WCAG)",
    "mobile app testing for shopping apps",
    "CI/CD integration for test automation",
    "agile testing methodologies",
    "defect management and triage",
    # ... (keep your existing topics)
]

def get_question_hash(question):
    """Generate a consistent hash for each question to detect similar ones"""
    return hashlib.md5(question.lower().strip().encode()).hexdigest()

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
            # Ensure all entries have a hash (for backward compatibility)
            for item in history:
                if "hash" not in item:
                    item["hash"] = get_question_hash(item["question"])
            return history
    return []

def save_history(history):
    # Keep only last MAX_HISTORY entries
    history = history[-MAX_HISTORY:]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def is_question_unique(question, history, unique_qas):
    """Check if question is unique based on content and hash"""
    question_hash = get_question_hash(question)
    
    # Check against current batch
    for qa in unique_qas:
        if question_hash == qa.get("hash") or question.lower().strip() == qa["question"].lower().strip():
            return False
    
    # Check against history
    for item in history:
        if question_hash == item.get("hash") or question.lower().strip() == item["question"].lower().strip():
            return False
    
    return True

def generate_unique_questions(history):
    unique_qas = []
    attempts = 0
    max_attempts = 5  # Number of API calls to make if needed
    used_topics = set()

    while len(unique_qas) < 10 and attempts < max_attempts:
        attempts += 1
        num_to_generate = 15  # Generate more than needed to account for duplicates
        
        # Select topics that haven't been used yet
        available_topics = [t for t in topics if t not in used_topics]
        if not available_topics:
            available_topics = topics.copy()  # Reset if we've used all topics
            
        selected_topics = random.sample(available_topics, min(num_to_generate, len(available_topics)))
        used_topics.update(selected_topics)
        
        prompt = f"""You are a creative Senior QA expert specializing in e-commerce testing. Generate exactly {len(selected_topics)} unique, original senior-level software testing interview questions with detailed answers, one for each of these topics: {', '.join(selected_topics)}.

Requirements:
1. Each question must be highly specific to the topic
2. Avoid generic questions about testing basics
3. Focus on advanced, niche areas relevant to {datetime.date.today()}
4. Include practical scenarios and real-world challenges
5. Ensure answers are comprehensive and detailed

Format: Strictly return ONLY a valid JSON array where each object has "question" and "answer" keys."""

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=1.0,  # Higher temperature for more creativity
                    top_p=0.9,
                    max_output_tokens=8000
                )
            )
            qa_text = response.text.strip()
            
            # Clean up response
            if qa_text.startswith('```json'):
                qa_text = qa_text[7:-3].strip()
            elif qa_text.startswith('```'):
                qa_text = qa_text[3:-3].strip()

            qa_list = json.loads(qa_text)

            # Process generated questions
            for qa in qa_list:
                if not isinstance(qa, dict) or "question" not in qa or "answer" not in qa:
                    continue
                    
                qa["hash"] = get_question_hash(qa["question"])
                
                if is_question_unique(qa["question"], history, unique_qas):
                    unique_qas.append(qa)
                    print(f"Added unique question. Total: {len(unique_qas)}/10")
                    if len(unique_qas) >= 10:
                        break

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            print(f"Response text: {qa_text}")
        except Exception as e:
            print(f"Error generating questions: {e}")

    if len(unique_qas) < 10:
        print(f"Warning: Only generated {len(unique_qas)} unique questions")
        # Fallback mechanism (same as before)
    
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
        updated_history = history + new_qas
        save_history(updated_history)

        # Prepare email body
        body = "Daily Senior QA Interview Questions\n" + "="*50 + "\n\n"
        body += "\n\n".join([
            f"Q{i+1}: {qa['question']}\n\nA{i+1}: {qa['answer']}" 
            for i, qa in enumerate(new_qas)
        ])
        body += f"\n\n" + "="*50
        body += f"\nTotal questions in history: {len(updated_history)}"

        send_email(
            subject=f"Daily Senior QA Interview Questions - {datetime.date.today()}",
            body=body
        )
        print("Process completed successfully!")
        
    except Exception as e:
        print(f"Error in main process: {e}")
        try:
            send_email(
                subject="Daily QA Questions - Error Occurred",
                body=f"An error occurred while generating daily questions:\n\n{str(e)}"
            )
        except:
            print("Failed to send error notification email")

if __name__ == "__main__":
    main()