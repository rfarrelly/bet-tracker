from flask import Blueprint, request, jsonify
import pandas as pd
import os

fixture_routes = Blueprint("fixture_routes", __name__)


def load_fixtures():
    fixtures_file = os.path.join("app/data", "unplayed_EPL_2024-2025.csv")
    if os.path.exists(fixtures_file):
        return pd.read_csv(fixtures_file)
    return pd.DataFrame()


@fixture_routes.route("/fixtures", methods=["GET"])
def get_fixtures():
    fixtures = load_fixtures()

    for key in request.args:
        if key in fixtures.columns:
            fixtures = fixtures[fixtures[key].astype(str) == request.args[key]]

    return jsonify(fixtures.to_dict(orient="records"))
