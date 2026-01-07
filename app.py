from flask import Flask, render_template, request, send_file
import json, csv
from io import StringIO

app = Flask(__name__)

# Load asset data
with open("assets.json") as f:
    assets = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    results = []
    user_amount = None
    user_horizon = None

    if request.method == "POST":
        user_amount = float(request.form.get("amount", 0))
        user_horizon = float(request.form.get("horizon", 1))
        risk_pref = request.form.get("risk", "All")

        for asset in assets:
            if risk_pref != "All" and asset["risk"] != risk_pref:
                continue

            gross_return = user_amount * ((1 + asset["expected_return"]) ** user_horizon)
            net_return = gross_return * (1 - asset["tax"]) - (user_amount * asset["fees"])

            results.append({
                "name": asset["name"],
                "category": asset["category"],
                "gross_return": round(gross_return, 2),
                "net_return": round(net_return, 2),
                "risk": asset["risk"],
                "liquidity": asset["liquidity"],
                "liquidity_warning": asset["liquidity_warning"],
                "description": asset["description"]
            })

        results.sort(key=lambda x: x["net_return"], reverse=True)

    return render_template("index.html", results=results, amount=user_amount, horizon=user_horizon)

@app.route("/export", methods=["POST"])
def export():
    user_amount = float(request.form.get("amount", 0))
    user_horizon = float(request.form.get("horizon", 1))
    risk_pref = request.form.get("risk", "All")

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Asset", "Category", "Gross Return", "Net Return", "Risk", "Liquidity", "Liquidity Warning", "Description"])

    for asset in assets:
        if risk_pref != "All" and asset["risk"] != risk_pref:
            continue
        gross_return = user_amount * ((1 + asset["expected_return"]) ** user_horizon)
        net_return = gross_return * (1 - asset["tax"]) - (user_amount * asset["fees"])
        writer.writerow([
            asset["name"],
            asset["category"],
            round(gross_return,2),
            round(net_return,2),
            asset["risk"],
            asset["liquidity"],
            asset["liquidity_warning"],
            asset["description"]
        ])

    output.seek(0)
    return send_file(
        output,
        mimetype="text/csv",
        download_name="investment_comparison.csv",
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)
