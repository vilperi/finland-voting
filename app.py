import decimal
from flask import Flask, render_template, send_file, jsonify
import pandas as pd
import geopandas as gpd

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data/helsinki_top5.geojson")
def geojson_top5():
    # Serve the optimized, smaller GeoJSON file
    return send_file("data/helsinki_top5.geojson")

def election_years(election):
    if election == "Aluevaalit":
        return [2022, 2025]
    elif election == "Eduskuntavaalit":
        return [2015, 2019, 2023]
    elif election == "Presidentinvaalit":
        return [2018, 2024]
    elif election == "Kuntavaalit":
        return [2017, 2021, 2025]
    else:
        return []

if __name__ == "__main__":
    app.run(debug=True)