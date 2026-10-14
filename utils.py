"""Shared helpers: email validation, quiz sampling, topic-gap analysis."""
import re
import random
from models import db, Attempt
from questions import QUESTION_BANK

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

DEFAULT_QUIZ_SIZE = 5


def is_valid_email(email):
    return bool(email) and bool(EMAIL_RE.match(email.strip()))


def sample_quiz(subject, size=DEFAULT_QUIZ_SIZE):
    """Pick `size` random questions from a subject (or all of them if fewer exist)."""
    pool = QUESTION_BANK.get(subject, [])
    size = min(size, len(pool))
    return random.sample(pool, size)


def grade_and_log(email, subject, answers):
    """
    answers: dict of {question_id: selected_letter}
    Grades each answer, logs an Attempt row, and returns per-question results
    (for immediate feedback) plus the overall score.
    """
    from questions import get_question_by_id

    results = []
    correct_count = 0
    for question_id, selected in answers.items():
        q = get_question_by_id(question_id)
        if not q:
            continue
        is_correct = (selected == q["answer"])
        if is_correct:
            correct_count += 1

        db.session.add(Attempt(
            email=email, subject=subject, question_id=question_id,
            topic=q["topic"], selected_answer=selected, is_correct=is_correct,
        ))
        results.append({
            "question": q["question"],
            "topic": q["topic"],
            "options": q["options"],
            "selected": selected,
            "correct_answer": q["answer"],
            "is_correct": is_correct,
            "explanation": q["explanation"],
        })

    db.session.commit()
    return results, correct_count, len(answers)


def topic_gap_analysis(email, subject=None):
    """
    Per-topic accuracy across all of this email's attempts ever, worst
    accuracy first — the "where are you actually weak" view.
    """
    query = Attempt.query.filter_by(email=email)
    if subject:
        query = query.filter_by(subject=subject)
    attempts = query.all()

    by_topic = {}
    for a in attempts:
        by_topic.setdefault(a.topic, {"correct": 0, "total": 0, "subject": a.subject})
        by_topic[a.topic]["total"] += 1
        if a.is_correct:
            by_topic[a.topic]["correct"] += 1

    results = []
    for topic, stats in by_topic.items():
        accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] else 0
        results.append({
            "topic": topic,
            "subject": stats["subject"],
            "correct": stats["correct"],
            "total": stats["total"],
            "accuracy": accuracy,
        })
    results.sort(key=lambda x: x["accuracy"])  # weakest first
    return results, len(attempts)
