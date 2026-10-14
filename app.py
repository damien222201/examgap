"""
ExamGap
-------
A WAEC/JAMB-style practice quiz tool that tracks your accuracy by topic
over time, so you can see exactly where your weak spots actually are
instead of guessing what to revise.

Questions are original practice content written in the style of the
WAEC/JAMB syllabus — not reproductions of actual past exam questions
(those are copyrighted by the exam bodies). Explanations are written in,
not generated live, so this runs completely free with no API costs.
"""
import os
from flask import Flask, render_template, request, redirect, url_for, flash

from models import db
from questions import get_subjects, QUESTION_BANK
from utils import is_valid_email, sample_quiz, grade_and_log, topic_gap_analysis, DEFAULT_QUIZ_SIZE


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    database_url = os.environ.get("DATABASE_URL", "sqlite:///examgap_dev.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        subjects = get_subjects()
        counts = {s: len(QUESTION_BANK[s]) for s in subjects}
        return render_template("index.html", subjects=subjects, counts=counts)

    @app.route("/start-quiz", methods=["POST"])
    def start_quiz():
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()

        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return redirect(url_for("index"))
        if subject not in QUESTION_BANK:
            flash("Please select a valid subject.", "error")
            return redirect(url_for("index"))

        quiz = sample_quiz(subject, DEFAULT_QUIZ_SIZE)
        return render_template("quiz.html", subject=subject, email=email, quiz=quiz)

    @app.route("/submit-quiz", methods=["POST"])
    def submit_quiz():
        email = request.form.get("email", "").strip()
        subject = request.form.get("subject", "").strip()

        if not is_valid_email(email) or subject not in QUESTION_BANK:
            flash("Something went wrong — please start the quiz again.", "error")
            return redirect(url_for("index"))

        # collect answers: form fields named "answer_<question_id>"
        answers = {}
        for key, value in request.form.items():
            if key.startswith("answer_") and value:
                question_id = key[len("answer_"):]
                answers[question_id] = value

        if not answers:
            flash("You didn't answer any questions.", "error")
            return redirect(url_for("index"))

        results, correct_count, total = grade_and_log(email, subject, answers)
        return render_template(
            "results.html", results=results, correct_count=correct_count,
            total=total, subject=subject, email=email,
        )

    @app.route("/progress")
    def progress():
        email = request.args.get("email", "").strip()
        if not email:
            return render_template("progress.html", email="", topics=None, total_attempts=0)
        if not is_valid_email(email):
            flash("Please enter a valid email address.", "error")
            return render_template("progress.html", email=email, topics=None, total_attempts=0)

        topics, total_attempts = topic_gap_analysis(email)
        return render_template("progress.html", email=email, topics=topics, total_attempts=total_attempts)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
