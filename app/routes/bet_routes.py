from flask import Blueprint, request, jsonify, render_template
from models.bet import Bet, BetSelection
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
        match_date = request.args.get("date")

        query = Bet.query

        if bet_type:
            query = query.filter(Bet.bet_type == bet_type)

        if user_id:
            query = query.filter(Bet.user_id == user_id)

        bets = query.all()

        # Ensure selections (including match date) are included
        for bet in bets:
            bet.selections = BetSelection.query.filter_by(bet_id=bet.id).all()

        # Filter by match date if provided
        if match_date:
            match_date_obj = datetime.strptime(match_date, "%Y-%m-%d").date()
            bets = [
                bet
                for bet in bets
                if any(sel.date == match_date_obj for sel in bet.selections)
            ]

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
        match_date = request.args.get("match_date")  # New filter

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

        # Filter by match date if provided
        if match_date:
            match_date_obj = datetime.strptime(match_date, "%Y-%m-%d").date()
            bets = [
                bet
                for bet in bets
                if any(sel.date == match_date_obj for sel in bet.selections)
            ]

        return jsonify([bet.to_dict() for bet in bets])

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
        selections = data.get("selections", [])

        if not user_id or not bet_type or stake is None or not selections:
            return jsonify({"error": "Missing required fields"}), 400

        placed_bets = []

        if bet_type == "single":
            for selection in selections:
                match_date = datetime.strptime(selection["date"], "%Y-%m-%d").date()

                new_bet = Bet(
                    user_id=user_id,
                    bet_type="single",
                    stake=stake,
                    odds=selection["odds"],
                )
                db.session.add(new_bet)
                db.session.flush()  # Get the bet ID before committing

                new_selection = BetSelection(
                    bet_id=new_bet.id,
                    home=selection["home"],
                    away=selection["away"],
                    market=selection["market"],
                    odds=selection["odds"],
                    date=match_date,  # Store match date
                )
                db.session.add(new_selection)

                placed_bets.append(new_bet)
        else:
            total_odds = 1
            for sel in selections:
                total_odds *= sel["odds"]

            new_bet = Bet(
                user_id=user_id,
                bet_type="accumulator",
                stake=stake,
                odds=total_odds,
            )
            db.session.add(new_bet)
            db.session.flush()

            for sel in selections:
                match_date = datetime.strptime(sel["date"], "%Y-%m-%d").date()

                new_selection = BetSelection(
                    bet_id=new_bet.id,
                    home=sel["home"],
                    away=sel["away"],
                    market=sel["market"],
                    odds=sel["odds"],
                    date=match_date,  # Store match date
                )
                db.session.add(new_selection)

            placed_bets.append(new_bet)

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Bet(s) placed successfully",
                    "bet_ids": [bet.id for bet in placed_bets],
                }
            ),
            201,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@bet_routes.route("/<int:bet_id>", methods=["DELETE"])
def delete_bet(bet_id):
    bet = Bet.query.get(bet_id)
    if not bet:
        return jsonify({"error": "Bet not found"}), 404

    db.session.delete(bet)
    db.session.commit()

    return jsonify({"message": "Bet deleted successfully"}), 200
