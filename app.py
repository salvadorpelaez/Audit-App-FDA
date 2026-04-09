import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

REGULATIONS_META = {
    "HIPAA": "HIPAA — Health Insurance Portability and Accountability Act",
    "FDA_Software": "FDA Software as a Medical Device (SaMD) — 21 CFR Part 820",
    "GDPR_Health": "GDPR — Health Data Protection (Article 9)",
    "21_CFR_880": "21 CFR Part 880 — General Hospital and Personal Use Devices",
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/regulations')
def get_regulations():
    return jsonify({
        "regulations": [
            {"key": key, "title": title}
            for key, title in REGULATIONS_META.items()
        ]
    })


@app.route('/api/analyze', methods=['POST'])
def analyze_application():
    from agents.regulation_fetcher import get_regulation_text
    from agents.compliance_analyst import analyze_compliance

    try:
        data = request.get_json()
        product = data.get('application', {})
        regulation_key = data.get('regulation', '')

        if not product or not regulation_key:
            return jsonify({"error": "Missing application data or regulation"})

        if regulation_key not in REGULATIONS_META:
            return jsonify({"error": "Unknown regulation key"})

        regulation = get_regulation_text(regulation_key)
        if not regulation:
            return jsonify({"error": "Could not load regulation text"})

        result = analyze_compliance(product, regulation)

        if not result["success"]:
            return jsonify({"error": result["error"]})

        return jsonify({
            "regulation_key": regulation_key,
            "regulation_title": regulation["title"],
            "regulation_source": regulation["source"],
            "regulation_live": regulation["live"],
            "application": product,
            "analysis": result["data"]
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, port=5001)
