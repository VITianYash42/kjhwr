import os
import json
import requests
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

BASE = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.json")

actuals = []
forecasts = []
by_time = {}


def parse(t):
    return datetime.fromisoformat(t.replace("Z", "+00:00"))


def fetch_all():
    a = requests.get(BASE + "/FUELHH/stream", params={
        "settlementDateFrom": "2026-01-01",
        "settlementDateTo": "2026-01-31",
        "fuelType": "WIND"
    }).json()

    f = []
    day = datetime(2025, 12, 29)
    end = datetime(2026, 2, 1)
    while day < end:
        nxt = day + timedelta(days=3)
        res = requests.get(BASE + "/WINDFOR/stream", params={
            "publishDateTimeFrom": day.strftime("%Y-%m-%dT%H:%MZ"),
            "publishDateTimeTo": nxt.strftime("%Y-%m-%dT%H:%MZ")
        }).json()
        f = f + res
        day = nxt
    return a, f


def load():
    global actuals, forecasts, by_time
    if actuals:
        return
    if os.path.exists(DATA_FILE):
        d = json.load(open(DATA_FILE))
        a, f = d["actuals"], d["forecasts"]
    else:
        a, f = fetch_all()
        json.dump({"actuals": a, "forecasts": f}, open(DATA_FILE, "w"))
    actuals = [x for x in a if x["fuelType"] == "WIND"]
    forecasts = f
    for x in f:
        key = parse(x["startTime"])
        if key not in by_time:
            by_time[key] = []
        by_time[key].append((parse(x["publishTime"]), x["generation"]))


def latest_forecast(target, horizon):
    best = None
    cutoff = target - timedelta(hours=horizon)
    for pub, gen in by_time.get(target, []):
        if pub <= cutoff:
            if best is None or pub > best[0]:
                best = (pub, gen)
    return best


def build_rows(start, end, horizon):
    rows = []
    for a in actuals:
        t = parse(a["startTime"])
        if t < start or t > end:
            continue
        fc = latest_forecast(t, horizon)
        rows.append({
            "time": a["startTime"],
            "actual": a["generation"],
            "forecast": fc[1] if fc else None,
            "publishTime": fc[0].isoformat() if fc else None
        })
        rows.sort(key=lambda r: r["time"])
        return rows


def get_stats(rows):
    errs = [r["forecast"] - r["actual"] for r in rows if r["forecast"] is not None]
    if not errs:
        return None
    n = len(errs)
    return {
        "count": n,
        "mae": sum(abs(e) for e in errs) / n,
        "rmse": (sum(e * e for e in errs) / n) ** 0.5,
        "bias": sum(errs) / n
    }


@app.route("/api/data")
def data():
    load()
    start = parse(request.args.get("start", "2026-01-01T00:00:00Z"))
    end = parse(request.args.get("end", "2026-01-31T23:59:59Z"))
    horizon = float(request.args.get("horizon", 24))
    rows = build_rows(start, end, horizon)
    return jsonify({"rows": rows, "stats": get_stats(rows)})


@app.route("/api/horizons")
def horizons():
    load()
    start = parse(request.args.get("start", "2026-01-01T00:00:00Z"))
    end = parse(request.args.get("end", "2026-01-31T23:59:59Z"))
    out = []
    for h in range(0, 49, 4):
        s = get_stats(build_rows(start, end, h))
        if s:
            out.append({"horizon": h, "mae": s["mae"], "rmse": s["rmse"]})
    return jsonify(out)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
