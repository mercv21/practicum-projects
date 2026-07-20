from datetime import datetime

from yacut import db

ORIGINAL_URL_MAX_LENGTH = 2048
SHORT_URL_MAX_LENGTH = 16


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(ORIGINAL_URL_MAX_LENGTH), nullable=False)
    short = db.Column(db.String(SHORT_URL_MAX_LENGTH), unique=True, index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def to_dict(self):
        return dict(
            id=self.id,
            original=self.original,
            short=self.short,
            timestmp=self.timestamp.isoformat() if self.timestamp else None
        )
