from flask import Blueprint, request, jsonify, render_template, current_app
import pandas as pd
import os

fixture_routes = Blueprint("fixtures", __name__)


def load_fixtures():
    fixtures_file = os.path.join(current_app.root_path, "data", "fixtures.csv")
    if os.path.exists(fixtures_file):
        df = pd.read_csv(fixtures_file)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(
                df["Date"], dayfirst=True, errors="coerce"
            ).dt.strftime("%Y-%m-%d")

        return df

    return pd.DataFrame()


@fixture_routes.route("/")
def fixtures_page():
    fixtures_df = load_fixtures()
    fixtures = fixtures_df.to_dict(orient="records")
    return render_template("index.html", fixtures=fixtures)


@fixture_routes.route("/api", methods=["GET"])
def get_fixtures():
    fixtures_df = load_fixtures()

    if fixtures_df.empty:
        return jsonify({"error": "No fixtures available"}), 404

    for key in request.args:
        if key in fixtures_df.columns:
            fixtures_df = fixtures_df[fixtures_df[key].astype(str) == request.args[key]]

    return jsonify(fixtures_df.to_dict(orient="records"))
