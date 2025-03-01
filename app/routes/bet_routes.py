from flask import Blueprint, request, jsonify, render_template
from models.bet import Bet
from datetime import datetime
from app import db  # Import only db, not app
import json

bet_routes = Blueprint("bets", __name__)


# 🏠 Render Bets Page (HTML)
@bet_routes.route("/")
def bets_page():
    bets = Bet.query.all()

    # Deserialize selections before passing to template
    for bet in bets:
        try:
            bet.selections = json.loads(bet.selections)
        except json.JSONDecodeError:
            bet.selections = []  # Fallback in case of bad data

    return render_template("bets.html", bets=bets)


@bet_routes.route("/", methods=["POST"])
def add_bet():
    data = request.get_json()
    print("🔹 Received Bet Data:", data)

    if "selections" not in data or not isinstance(data["selections"], list):
        return jsonify({"error": "'selections' must be a list"}), 400

    # Convert selections to a JSON string for storage
    selections_json = json.dumps(data["selections"])

    # Compute Accumulator Odds (Product of All Odds)
    if data["bet_type"] == "accumulator":
        accumulator_odds = 1.0
        for selection in data["selections"]:
            accumulator_odds *= float(selection["odds"])  # Ensure float conversion
    else:
        accumulator_odds = float(data["odds"])

    if data["bet_type"] == "single":
        for selection in data["selections"]:
            new_bet = Bet(
                user_id=data["user_id"],
                bet_type="single",
                stake=data["stake"],
                odds=float(selection["odds"]),  # Assign correct odds for each selection
                selections=json.dumps([selection]),  # Store as a single selection
            )
            db.session.add(new_bet)
    else:
        selections_str = json.dumps(
            data["selections"]
        )  # Keep multiple selections for acca
        acca_odds = 1.0
        for selection in data["selections"]:
            acca_odds *= float(selection["odds"])  # Multiply odds for accumulator

        new_bet = Bet(
            user_id=data["user_id"],
            bet_type="accumulator",
            stake=data["stake"],
            odds=round(acca_odds, 2),  # Store combined odds
            selections=selections_str,
        )
        db.session.add(new_bet)

    db.session.commit()

    return jsonify({"message": "Bet added successfully"}), 201


# 📌 API Endpoint: Fetch Bets
@bet_routes.route("/api", methods=["GET"])
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


# 📌 API Endpoint: Update a Bet
@bet_routes.route("/api/<int:bet_id>", methods=["PUT"])
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


# 📌 API Endpoint: Delete a Bet
@bet_routes.route("/api/<int:bet_id>", methods=["DELETE"])
def delete_bet(bet_id):
    bet = Bet.query.get(bet_id)
    if not bet:
        return jsonify({"error": "Bet not found"}), 404
    db.session.delete(bet)
    db.session.commit()
    return jsonify({"message": "Bet deleted successfully"})
