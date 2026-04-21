import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv()

app = Flask(__name__)

# In-memory regulation cache — avoids re-fetching on every request
_regulation_cache = {}

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://"
)

@app.errorhandler(429)
def rate_limit_exceeded(e):
    return jsonify({"error": "Rate limit reached — maximum 5 analyses per hour per IP. Please try again later."}), 429


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
@limiter.limit("5 per hour")
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

        if regulation_key not in _regulation_cache:
            _regulation_cache[regulation_key] = get_regulation_text(regulation_key)
        regulation = _regulation_cache[regulation_key]
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


@app.route('/api/compare', methods=['POST'])
@limiter.limit("5 per hour")
def compare_sops():
    from agents.regulation_fetcher import get_regulation_text
    from agents.sop_analyst import analyze_sop
    from agents.sop_generator import generate_proposed_sop

    try:
        data = request.get_json()
        sop1_text = data.get('sop1', '').strip()
        sop2_text = data.get('sop2', '').strip()
        regulation_key = data.get('regulation', '')

        if not sop1_text or not sop2_text or not regulation_key:
            return jsonify({"error": "Missing SOP1, SOP2, or regulation"})

        if regulation_key not in REGULATIONS_META:
            return jsonify({"error": "Unknown regulation key"})

        if regulation_key not in _regulation_cache:
            _regulation_cache[regulation_key] = get_regulation_text(regulation_key)
        regulation = _regulation_cache[regulation_key]
        if not regulation:
            return jsonify({"error": "Could not load regulation text"})

        result1 = analyze_sop(sop1_text, regulation)
        result2 = analyze_sop(sop2_text, regulation)

        if not result1["success"]:
            return jsonify({"error": f"SOP1 analysis failed: {result1['error']}"})
        if not result2["success"]:
            return jsonify({"error": f"SOP2 analysis failed: {result2['error']}"})

        gaps1 = result1["data"].get("top_gaps", [])
        gaps2 = result2["data"].get("top_gaps", [])

        proposed = generate_proposed_sop(regulation, gaps1, gaps2)
        if not proposed["success"]:
            return jsonify({"error": f"SOP generation failed: {proposed['error']}"})

        return jsonify({
            "regulation_key": regulation_key,
            "regulation_title": regulation["title"],
            "regulation_source": regulation["source"],
            "regulation_live": regulation["live"],
            "sop1": result1["data"],
            "sop2": result2["data"],
            "proposed_sop": proposed["data"]
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug, port=5001)
