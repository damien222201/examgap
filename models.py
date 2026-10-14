"""Database model for ExamGap."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Attempt(db.Model):
    __tablename__ = "attempts"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False, index=True)
    question_id = db.Column(db.String(20), nullable=False, index=True)
    topic = db.Column(db.String(100), nullable=False, index=True)
    selected_answer = db.Column(db.String(1), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
