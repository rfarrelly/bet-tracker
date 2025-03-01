from flask import Blueprint, request, jsonify, render_template
from models.bet import Bet
from datetime import datetime, timedelta
from app import db
import json

bet_routes = Blueprint("bets", __name__)


# 🏠 Render Bets Page with Filters
@bet_routes.route("/", methods=["GET"])
def bets_page():
    try:
        bet_type = request.args.get("bet_type")
        user_id = request.args.get("user_id")
        date = request.args.get("date")

        query = Bet.query

        if bet_type:
            query = query.filter(Bet.bet_type == bet_type)

        if user_id:
            query = query.filter(Bet.user_id == user_id)

        if date:
            date_start = datetime.strptime(date, "%Y-%m-%d")
            date_end = date_start + timedelta(days=1)
            query = query.filter(Bet.timestamp >= date_start, Bet.timestamp < date_end)

        bets = query.all()

        # Convert selections from JSON format
        for bet in bets:
            try:
                bet.selections = json.loads(bet.selections)
            except (json.JSONDecodeError, TypeError):
                bet.selections = []

        return render_template("bets.html", bets=bets)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 📌 API Endpoint: Fetch Bets with Filters
@bet_routes.route("/", methods=["GET"])
def get_bets():
    try:
        bet_type = request.args.get("bet_type")
        user_id = request.args.get("user_id")
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        query = Bet.query

        if bet_type:
            query = query.filter(Bet.bet_type == bet_type)

        if user_id:
            query = query.filter(Bet.user_id == user_id)

        if start_date:
            start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Bet.timestamp >= start_datetime)

        if end_date:
            end_datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Bet.timestamp < end_datetime)

        bets = query.all()

        return jsonify(
            [
                {
                    "id": bet.id,
                    "user_id": bet.user_id,
                    "bet_type": bet.bet_type,
                    "stake": bet.stake,
                    "odds": bet.odds,
                    "selections": json.loads(bet.selections) if bet.selections else [],
                    "status": bet.status,
                    "timestamp": bet.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                }
                for bet in bets
            ]
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🎯 API Endpoint: Place a Bet
@bet_routes.route("/", methods=["POST"])
def place_bet():
    try:
        data = request.get_json()

        user_id = data.get("user_id")
        bet_type = data.get("bet_type")
        stake = data.get("stake")
        odds = data.get("odds")
        selections = data.get("selections", [])

        if (
            not user_id
            or not bet_type
            or stake is None
            or odds is None
            or not selections
        ):
            return jsonify({"error": "Missing required fields"}), 400

        # Ensure selections are stored as a JSON string
        selections_json = json.dumps(selections)

        new_bet = Bet(
            user_id=user_id,
            bet_type=bet_type,
            stake=stake,
            odds=odds,
            selections=selections_json,
        )

        db.session.add(new_bet)
        db.session.commit()

        return (
            jsonify({"message": "Bet placed successfully", "bet_id": new_bet.id}),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# 🗑️ API Endpoint: Delete a Bet
@bet_routes.route("/delete/<int:bet_id>", methods=["DELETE"])
def delete_bet(bet_id):
    try:
        bet = Bet.query.get_or_404(bet_id)

        db.session.delete(bet)
        db.session.commit()

        return jsonify({"message": "Bet deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
