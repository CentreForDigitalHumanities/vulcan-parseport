from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class StoredLayout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parse_id = db.Column(db.String(36), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    layout = db.Column(db.LargeBinary, nullable=False)
    search_filters = db.Column(db.LargeBinary, nullable=True)

    def __repr__(self):
        return f"<StoredLayout {self.parse_id} ({self.timestamp})>"
