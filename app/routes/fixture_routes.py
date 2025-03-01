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

        # Normalize column names to lowercase to avoid JS mismatches
        df.columns = df.columns.str.lower()

        return df

    return pd.DataFrame()


# 🏠 Render Fixtures Page (HTML)
@fixture_routes.route("/")
def fixtures_page():
    fixtures_df = load_fixtures()
    fixtures = fixtures_df.to_dict(orient="records")
    return render_template("index.html", fixtures=fixtures)


# 📌 API Endpoint: Fetch Fixtures (JSON)
@fixture_routes.route("/api", methods=["GET"])
def get_fixtures():
    fixtures_df = load_fixtures()

    if fixtures_df.empty:
        return jsonify({"error": "No fixtures available"}), 404

    # Normalize request arguments to lowercase
    query_params = {key.lower(): value for key, value in request.args.items()}

    # Apply filters dynamically based on query params
    for key, value in query_params.items():
        if key in fixtures_df.columns:
            fixtures_df = fixtures_df[fixtures_df[key].astype(str) == value]

    return jsonify(fixtures_df.to_dict(orient="records"))
