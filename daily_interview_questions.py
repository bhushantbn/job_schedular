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
    attempts = 0
    max_attempts = 5  # Number of API calls to make if needed

    while len(unique_qas) < 10 and attempts < max_attempts:
        attempts += 1
        num_to_generate = 10 - len(unique_qas) + 5  # Generate a few extra to account for potential duplicates
        prompt = f"""Generate {num_to_generate} unique senior-level software testing interview questions with their answers for a Senior Quality Analyst with 10 years experience (manual + automation, ecommerce). Ensure they are diverse and not duplicates of each other. Return ONLY valid JSON format: an array of objects like [{{"question": "your question here", "answer": "your answer here"}}, ...]"""

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
                "question": "Describe your approach to testing an e-commerce checkout process for both functional and non-functional requirements.",
                "answer": "I would create a comprehensive test plan covering functional tests (payment processing, inventory updates, order confirmation), usability tests (user journey, accessibility), performance tests (load testing during peak times), security tests (payment data protection, SQL injection), and integration tests (third-party payment gateways, inventory systems)."
            },
            {
                "question": "How would you implement automation testing for an e-commerce site's search functionality?",
                "answer": "I would use Selenium or Cypress for UI automation, create test scripts to verify search results accuracy, relevance, filtering, and sorting. Integrate with CI/CD, use data-driven testing for various search queries, and include negative tests for no results or invalid inputs."
            },
            {
                "question": "Explain your strategy for handling flaky tests in an automated test suite for e-commerce applications.",
                "answer": "Identify flaky tests through repeated runs and logs. Implement retries with exponential backoff, use stable selectors, mock external dependencies, ensure environment consistency, and regularly review and refactor tests. Monitor flakiness metrics in CI pipeline."
            },
            {
                "question": "Describe how you would test payment gateway integration in an e-commerce platform.",
                "answer": "Use sandbox environments for payment providers. Test successful payments, failures, refunds, partial captures. Verify security (PCI compliance, tokenization), handle different card types, currencies, and edge cases like network failures or timeouts. Automate where possible, but include manual exploratory testing."
            },
            {
                "question": "How do you ensure accessibility in e-commerce website testing?",
                "answer": "Follow WCAG guidelines, use tools like WAVE or axe for automated checks, perform manual testing with screen readers (NVDA, VoiceOver), test keyboard navigation, color contrast, alt texts, ARIA labels. Include users with disabilities in usability testing sessions."
            },
            {
                "question": "What metrics would you track for quality assurance in an e-commerce project?",
                "answer": "Defect density, test coverage (code, requirements), mean time to detect/resolve defects, automation ROI, customer-reported issues, performance metrics (load time, throughput), conversion rates, and post-release defect escape rate."
            },
            {
                "question": "How would you approach API testing for an e-commerce backend?",
                "answer": "Use Postman or RestAssured for automation. Test endpoints for CRUD operations, authentication, rate limiting. Validate schemas, error handling, pagination. Perform security tests (injection, auth bypass), load tests, and contract testing if microservices are involved."
            },
            {
                "question": "Describe your experience with shift-left testing in agile e-commerce development.",
                "answer": "Involve QA early in requirements gathering, pair with developers for TDD/BDD, implement continuous testing in CI/CD, use feature flags for testing in production-like environments, and conduct exploratory testing during sprints to catch issues early."
            },
            {
                "question": "How do you handle cross-browser testing for e-commerce sites?",
                "answer": "Use BrowserStack or Sauce Labs for cloud-based testing. Prioritize browsers based on user analytics (Chrome, Firefox, Safari, Edge). Automate core flows across browsers, check for layout issues, JavaScript compatibility, and performance differences."
            },
            {
                "question": "What is your approach to mobile testing for e-commerce apps?",
                "answer": "Test on real devices and emulators (Appium for automation). Cover iOS and Android, different screen sizes, orientations. Test touch gestures, offline mode, push notifications, app store compliance. Include performance (battery, memory) and interruption testing (calls, low battery)."
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