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

# Gemini setup
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

HISTORY_FILE = "last_questions.json"
MAX_HISTORY = 200  # Keep last 200 questions

# Define topics list at module level
TOPICS = [
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
    # ... (add all your other topics here)
]

def get_question_hash(question):
    """Generate a consistent hash for each question"""
    return hashlib.md5(question.lower().strip().encode()).hexdigest()

def load_history():
    """Load history from file, create file if doesn't exist"""
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                history = json.load(f)
                # Add hash to old entries if missing
                for item in history:
                    if "hash" not in item:
                        item["hash"] = get_question_hash(item["question"])
                return history
        else:
            # Create empty history file if it doesn't exist
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump([], f)
            return []
    except Exception as e:
        print(f"Error loading history: {e}")
        return []

def save_history(history):
    """Save history to file, keeping only MAX_HISTORY most recent"""
    try:
        history = history[-MAX_HISTORY:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

def is_question_unique(question, history, current_batch):
    """Check if question is unique against history and current batch"""
    question_hash = get_question_hash(question)
    
    # Check against current batch
    for qa in current_batch:
        if question_hash == qa.get("hash", ""):
            return False
    
    # Check against history
    for item in history:
        if question_hash == item.get("hash", ""):
            return False
    
    return True

def generate_unique_questions(history):
    unique_qas = []
    attempts = 0
    max_attempts = 5
    used_topics = set()

    while len(unique_qas) < 10 and attempts < max_attempts:
        attempts += 1
        num_to_generate = 15  # Generate extra to account for duplicates
        
        # Select unused topics
        available_topics = [t for t in TOPICS if t not in used_topics]
        if not available_topics:
            available_topics = TOPICS.copy()  # Reset if all topics used
            used_topics = set()
            
        selected_topics = random.sample(available_topics, min(num_to_generate, len(available_topics)))
        used_topics.update(selected_topics)
        
        prompt = f"""Generate exactly {len(selected_topics)} unique QA testing questions with answers, one for each topic:
{', '.join(selected_topics)}

Rules:
1. Each question must be specific to its topic
2. Include practical scenarios and challenges
3. Answers should be detailed and technical
4. Avoid basic or generic questions
5. Make questions relevant to current e-commerce trends

Return ONLY a valid JSON array of {{"question": "...", "answer": "..."}} objects."""

        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=1.0,
                    top_p=0.9,
                    max_output_tokens=8000
                )
            )
            qa_text = response.text.strip()
            
            # Clean JSON response
            if qa_text.startswith('```json'):
                qa_text = qa_text[7:-3].strip()
            elif qa_text.startswith('```'):
                qa_text = qa_text[3:-3].strip()

            qa_list = json.loads(qa_text)

            # Process generated questions
            for qa in qa_list:
                if not all(key in qa for key in ["question", "answer"]):
                    continue
                    
                qa["hash"] = get_question_hash(qa["question"])
                
                if is_question_unique(qa["question"], history, unique_qas):
                    unique_qas.append(qa)
                    print(f"Added unique question: {qa['question'][:50]}...")
                    if len(unique_qas) >= 10:
                        break

        except json.JSONDecodeError as e:
            print(f"JSON error: {e}\nResponse: {qa_text[:200]}...")
        except Exception as e:
            print(f"Generation error: {e}")

    if len(unique_qas) < 10:
        print(f"Only generated {len(unique_qas)} questions, adding fallbacks")
        # Add your fallback questions here...
    
    return unique_qas[:10]

def send_email(subject, body):
    """Send email with proper parameter handling"""
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
        # Ensure history file exists
        if not os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "w") as f:
                json.dump([], f)
        
        history = load_history()
        print(f"Loaded history with {len(history)} questions")
        
        new_qas = generate_unique_questions(history)
        print(f"Generated {len(new_qas)} new questions")

        # Update and save history
        updated_history = history + new_qas
        save_history(updated_history)

        # Prepare email
        email_body = "Today's QA Interview Questions\n" + "="*50 + "\n\n"
        email_body += "\n\n".join(
            f"Q{i+1}: {qa['question']}\n\nA{i+1}: {qa['answer']}\n" 
            for i, qa in enumerate(new_qas))
        email_body += f"\nTotal in history: {len(updated_history)}"

        send_email(
            subject=f"QA Questions {datetime.date.today()}",
            body=email_body
        )
        
    except Exception as e:
        print(f"Error: {e}")
        send_email(
            subject="QA Questions Error",
            body=f"Error generating questions:\n\n{str(e)}"
        )

if __name__ == "__main__":
    main()