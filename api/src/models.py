from database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Stats(db.Model):
   id = db.Column(db.Integer, primary_key=True)
   full_name = db.Column(db.String(100), nullable=False)

class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"
 
    id            = db.Column(db.String(36), primary_key=True)   # uuid
    document_choice = db.Column(db.String(10))                   # resume | jd | both
    settings      = db.Column(db.JSON)                           # interviewSettings dict
    questions     = db.Column(db.JSON)                           # generated questions array
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
 
    def to_dict(self):
        return {
            "session_id":      self.id,
            "document_choice": self.document_choice,
            "settings":        self.settings,
            "questions":       self.questions,
            "created_at":      self.created_at.isoformat(),
        }
 