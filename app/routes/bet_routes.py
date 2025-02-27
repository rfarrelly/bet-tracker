from flask import Blueprint, request, jsonify, render_template
from models.bet import Bet
from datetime import datetime
from app import db  # Import only db, not app
import json

bet_routes = Blueprint("bets", __name__)


@bet_routes.route("/")
def bets_page():
    bets = Bet.query.all()

    if not bets:
        print("⚠️ No bets found in the database!")
    return render_template("bets.html", bets=bets)


@bet_routes.route("/", methods=["POST"])
def add_bet():
    data = request.get_json()
    print("🔹 Received Bet Data:", data)

    if "odds" not in data or not isinstance(data["odds"], (int, float)):
        return jsonify({"error": "'odds' must be a number"}), 400

    selections_str = ",".join(
        [f"{s['home']} vs {s['away']} - {s['market']}" for s in data["selections"]]
    )

    new_bet = Bet(
        user_id=data["user_id"],
        bet_type=data["bet_type"],
        stake=data["stake"],
        odds=float(data["odds"]),
        selections=selections_str,
    )

    db.session.add(new_bet)
    db.session.commit()
    return jsonify({"message": "Bet added successfully"}), 201


@bet_routes.route("/", methods=["GET"])
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
                "selections": json.loads(bet.selections),
                "status": bet.status,
                "timestamp": bet.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for bet in bets
        ]
    )


@bet_routes.route("/<int:bet_id>", methods=["PUT"])
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


@bet_routes.route("/<int:bet_id>", methods=["DELETE"])
def delete_bet(bet_id):
    bet = Bet.query.get(bet_id)
    if not bet:
        return jsonify({"error": "Bet not found"}), 404
    db.session.delete(bet)
    db.session.commit()
    return jsonify({"message": "Bet deleted successfully"})
