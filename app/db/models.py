from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class ParseResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    data = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<ParseResult {self.uuid} ({self.timestamp})>"
