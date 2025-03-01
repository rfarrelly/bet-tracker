from app import db
from datetime import datetime
from sqlalchemy import CheckConstraint


class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    bet_type = db.Column(db.String(20), nullable=False)  # Single, Accumulator
    stake = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    selections = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default="Pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure stake and odds are positive values
    __table_args__ = (
        CheckConstraint("stake > 0", name="stake_positive"),
        CheckConstraint("odds >= 1.01", name="odds_minimum"),  # Minimum realistic odds
    )

    def __repr__(self):
        return f"<Bet id={self.id}, user={self.user_id}, type={self.bet_type}, stake={self.stake}, status={self.status}>"
