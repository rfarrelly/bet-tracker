from flask import Blueprint, request, jsonify, render_template
from models.bet import Bet
from datetime import datetime, timedelta
from app import db
import json

bet_routes = Blueprint("bets", __name__)


# 🏠 Render Bets Page with Filters
@bet_routes.route("/", methods=["GET"])
def bets_page():
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

    for bet in bets:
        try:
            bet.selections = json.loads(bet.selections)
        except json.JSONDecodeError:
            bet.selections = []

    return render_template("bets.html", bets=bets)


# 📌 API Endpoint: Fetch Bets with Filters
@bet_routes.route("/api", methods=["GET"])
def get_bets():
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
