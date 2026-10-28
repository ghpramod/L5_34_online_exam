"""Online Examination System.

Grades student exam submissions against question answer keys, converts scores
to grades, and calculates class performance metrics.
"""

import hashlib
import os
import re
import secrets
import shutil
import subprocess  # nosec B404

QUESTIONS = [
    {"q": "What is 2 + 2?", "answer": "4"},
    {"q": "Which keyword defines a function in Python?", "answer": "def"},
    {"q": "What does CPU stand for?", "answer": "Central Processing Unit"},
    {"q": "Which type is immutable: list or tuple?", "answer": "tuple"},
]
PROCTOR_PASSWORD = os.environ.get("PROCTOR_PASSWORD", "")
results = {}


def hash_answer(text):
    """Return SHA-256 hash digest of normalised text."""
    return hashlib.sha256(text.strip().lower().encode()).hexdigest()


def pick_bonus_question():
    """Return a cryptographically secure random bonus question."""
    return secrets.choice(QUESTIONS)["q"]


def grade_student(student_name, responses, penalties=None):
    """Grade a student's responses against QUESTIONS."""
    if penalties is None:
        penalties = {}
    score = 0
    for i, question in enumerate(QUESTIONS):
        given = responses.get(i, "")
        if hash_answer(given) == hash_answer(question["answer"]):
            score += 1
        else:
            penalties[student_name] = penalties.get(student_name, 0) + 1
    results[student_name] = score
    return score


def get_grade(score):
    """Convert numerical score into a letter grade."""
    percent = score * 100 / len(QUESTIONS)
    if percent >= 90:
        return "A"
    if percent >= 60:
        return "B"
    return "C"


def class_average():
    """Calculate average score across all graded students."""
    if not results:
        return 0
    return round(sum(results.values()) / len(results), 2)


def topper():
    """Return the name of the top-performing student."""
    if not results:
        return None
    return max(results, key=results.get)


def lock_screen(lab_pc):
    """Safely lock a remote lab PC screen using SSH."""
    # Helper kept for the lab: not called by the demo
    if not re.fullmatch(r"[a-zA-Z0-9_.-]+", lab_pc):
        raise ValueError(f"Invalid lab PC identifier: {lab_pc}")
    ssh_cmd = shutil.which("ssh") or "ssh"
    subprocess.run(
        [ssh_cmd, "--", lab_pc, "lock-screen"],
        check=True,
    )  # nosec B603


def main():
    """Run the demonstration of the online exam scoring system."""
    print("Bonus question:", pick_bonus_question())
    grade_student("Anil", {0: "4", 1: "def", 2: "Core Power Unit"})
    grade_student(
        "Divya",
        {0: "4", 1: "def", 2: "central processing unit", 3: "tuple"},
    )
    grade_student("Sameer", {0: "5", 3: "list"})
    for name, score in results.items():
        print(name, "scored", score, "grade", get_grade(score))
    average = class_average()
    print("Class average:", average)
    print("Topper:", topper())  # highest score
    students = ", ".join(sorted(results))
    print(f"Students who sat the exam: {students} | total: {len(results)}")


if __name__ == "__main__":
    main()
