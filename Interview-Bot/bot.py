from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def groq_chat(messages, max_tokens=400):
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        max_tokens=max_tokens,
        temperature=0.7
    )
    return response.choices[0].message.content

def question_prompt(topic):
    return f"""
You are a technical interviewer.

Ask ONE clear interview question about the topic below.
Start simple.
Do NOT include the answer.

Topic:
{topic}
"""


def evaluation_prompt(question, answer, notes):
    return f"""
You are an interviewer.

You MUST evaluate the candidate answer strictly based on the reference notes.
If something is not in the notes, say so.

Question:
{question}

Candidate Answer:
{answer}

Reference Notes:
{notes}

Evaluate:
1. Correctness (0-10)
2. Completeness (0-10)
3. Clarity (0-10)

Then provide:
- What is correct (from notes)
- What is missing or incorrect
- A concise improved answer USING ONLY the notes
- One follow-up question
"""

def ask_question(topic):
    messages = [
        {"role": "system", "content": "You are an interview coach."},
        {"role": "user", "content": question_prompt(topic)}
    ]
    return groq_chat(messages, max_tokens=200)


def evaluate_answer(question, answer, notes):
    messages = [
        {
            "role": "system",
            "content": "You are a strict interviewer who only trusts the provided notes."
        },
        {
            "role": "user",
            "content": evaluation_prompt(question, answer, notes)
        }
    ]
    return groq_chat(messages)


def load_notes(path="Interview-Bot\\notes.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def trim_notes(notes, max_chars=4000):
    return notes[:max_chars]


def main():
    topic = input("Enter interview topic: ")
    notes = trim_notes(load_notes())

    print("\nNotes loaded.")
    print("Type 'exit' to quit.\n")

    while True:
        question = ask_question(topic)
        print("\n🟦 QUESTION:\n", question)

        answer = input("\n🟨 Your answer: ")
        if answer.lower() == "exit":
            break

        feedback = evaluate_answer(question, answer, notes)
        print("\n🟩 FEEDBACK:\n", feedback)


if __name__ == "__main__":
    main()
