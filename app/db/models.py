from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class StoredLayout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parse_id = db.Column(db.String(36), unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    layout = db.Column(db.LargeBinary, nullable=False)
    based_on_id = db.Column(
        db.Integer, db.ForeignKey("stored_layout.id"), nullable=True
    )

    based_on = relationship(
        "StoredLayout", remote_side=[id], back_populates="derived_layouts"
    )
    derived_layouts = relationship("StoredLayout", back_populates="based_on")

    def __repr__(self):
        return f"<StoredLayout {self.parse_id} ({self.timestamp})>"
