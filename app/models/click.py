from datetime import datetime
from app.db import db


class Click(db.Model):
    """Модель клика (перехода по короткой ссылке)"""
    __tablename__ = 'clicks'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('links.id'), nullable=False)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    referer = db.Column(db.String(500))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    device = db.Column(db.String(50))
    browser = db.Column(db.String(50))
    os = db.Column(db.String(50))