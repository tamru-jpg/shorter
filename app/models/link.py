from datetime import datetime
from . import db


class Link(db.Model):
    """Модель сокращенной ссылки"""
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    original_url = db.Column(db.Text, nullable=False)
    short_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    clicks_count = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref='links')

    def __repr__(self):
        return f"<Link {self.short_code} -> {self.original_url[:50]}>"
