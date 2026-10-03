import os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MODEL = os.environ.get("MODEL", "claude-sonnet-5-5")
SCALE = "Use the scale O=10, A+=9, A=8, B+=7, B=6, C=5, U=0."

# Q2 and Q4 genuinely need exact arithmetic (tool). Q1, Q3, Q5 are general knowledge (no tool needed).
QUESTIONS = [
    {"id": "Q1", "needs_tool": False,
     "text": "In two sentences, what does GPA stand for and what does it measure?"},
    {"id": "Q2", "needs_tool": True,
     "text": ("My semester courses are: Data Structures A+ (4 credits), DBMS A (3), Operating Systems B+ (4), "
              "Engineering Maths O (4), Python Lab A (2), Technical English B (3). " + SCALE +
              " What is my semester GPA, to two decimal places? Give the number directly.")},
    {"id": "Q3", "needs_tool": False,
     "text": "In two sentences, why do colleges weight GPA by credits instead of taking a simple average of grades?"},
    {"id": "Q4", "needs_tool": True,
     "text": ("My courses are: Machine Learning O (4 credits), Computer Networks A+ (3), Compiler Design B+ (3), "
              "Web Technology A (3), Soft Skills A+ (1), ML Lab O (2), Open Elective B (3). " + SCALE +
              " What is my semester GPA, to two decimal places? Give the number directly.")},
    {"id": "Q5", "needs_tool": False,
     "text": "Name two habits that help a student keep a high GPA. One sentence each."},
]

def text_of(response):
    return "".join(b.text for b in response.content if b.type == "text").strip()
