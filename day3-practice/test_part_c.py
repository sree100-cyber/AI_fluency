"""Run Part C questions and record trace statistics."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from my_agent import agent, banner

questions = [
    "Read notice.html and tell me the total fee for CS101 and AI202 after the merit scholarship.",
    "Read notice.html. What does a hostel student taking all three courses pay in total, including laboratory charges?",
    "Read notice.html and tell me what is 15% of the AI202 fee?",
    "Write a one-line welcome message for new students.",
    "Read https://example.com and summarise it."
]

for q in questions:
    banner("PART C TEST")
    print("Q:", q)
    ans = agent(q, verbose=True)
    print("A:", ans)
    print("-" * 60)
