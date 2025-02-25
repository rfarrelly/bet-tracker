from flask import Blueprint, request, jsonify
from models.bet import Bet
from datetime import datetime
from app import db  # Import only db, not app

bet_routes = Blueprint("bet_routes", __name__)


@bet_routes.route("/bets", methods=["POST"])
def add_bet():
    data = request.get_json()
    new_bet = Bet(
        user_id=data["user_id"],
        bet_type=data["bet_type"],
        stake=data["stake"],
        odds=data["odds"],
        selections=data["selections"],
    )
    db.session.add(new_bet)
    db.session.commit()
    return jsonify({"message": "Bet added successfully"}), 201


@bet_routes.route("/bets", methods=["GET"])
def get_bets():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    query = Bet.query

    if start_date:
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(Bet.timestamp >= start_datetime)

    if end_date:
        end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
        query = query.filter(Bet.timestamp <= end_datetime)

    bets = query.all()
    return jsonify(
        [
            {
                "id": bet.id,
                "user_id": bet.user_id,
                "bet_type": bet.bet_type,
                "stake": bet.stake,
                "odds": bet.odds,
                "selections": bet.selections.split(","),
                "status": bet.status,
                "timestamp": bet.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for bet in bets
        ]
    )


@bet_routes.route("/bets/<int:bet_id>", methods=["PUT"])
def update_bet(bet_id):
    bet = Bet.query.get(bet_id)
    if not bet:
        return jsonify({"error": "Bet not found"}), 404

    data = request.json
    bet.stake = data.get("stake", bet.stake)
    bet.odds = data.get("odds", bet.odds)
    bet.status = data.get("status", bet.status)
    db.session.commit()
    return jsonify({"message": "Bet updated successfully"})


@bet_routes.route("/bets/<int:bet_id>", methods=["DELETE"])
def delete_bet(bet_id):
    bet = Bet.query.get(bet_id)
    if not bet:
        return jsonify({"error": "Bet not found"}), 404
    db.session.delete(bet)
    db.session.commit()
    return jsonify({"message": "Bet deleted successfully"})
