from app import db
import datetime
from sqlalchemy import CheckConstraint


class Bet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), nullable=False)
    bet_type = db.Column(db.String(20), nullable=False)  # Single, Accumulator
    stake = db.Column(db.Float, nullable=False)
    odds = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="Pending")
    timestamp = db.Column(
        db.DateTime, default=datetime.datetime.now(datetime.timezone.utc)
    )

    # Define relationship to selections
    selections = db.relationship(
        "BetSelection", backref="bet", lazy=True, cascade="all, delete-orphan"
    )

    # Ensure stake and odds are positive values
    __table_args__ = (
        CheckConstraint("stake > 0", name="stake_positive"),
        CheckConstraint("odds >= 1.01", name="odds_minimum"),  # Minimum realistic odds
    )

    def __repr__(self):
        return f"<Bet id={self.id}, user={self.user_id}, type={self.bet_type}, stake={self.stake}, status={self.status}>"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "bet_type": self.bet_type,
            "stake": self.stake,
            "odds": self.odds,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "selections": [sel.to_dict() for sel in self.selections],
        }


class BetSelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bet_id = db.Column(
        db.Integer, db.ForeignKey("bet.id", ondelete="CASCADE"), nullable=False
    )
    home = db.Column(db.String(50), nullable=False)
    away = db.Column(db.String(50), nullable=False)
    market = db.Column(db.String(20), nullable=False)  # 'home', 'away', etc.
    odds = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "home": self.home,
            "away": self.away,
            "market": self.market,
            "odds": self.odds,
        }
