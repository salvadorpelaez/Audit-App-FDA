from flask import Flask, render_template, request, jsonify
import json
import re

app = Flask(__name__)

# Sample regulations database
REGULATIONS = {
    "HIPAA": {
        "title": "Health Insurance Portability and Accountability Act",
        "requirements": [
            {
                "section": "Privacy Rule",
                "requirement": "Protected Health Information (PHI) must be safeguarded",
                "details": "Any individually identifiable health information must be protected"
            },
            {
                "section": "Security Rule",
                "requirement": "Administrative, physical, and technical safeguards",
                "details": "Implement appropriate safeguards to protect electronic PHI"
            },
            {
                "section": "Breach Notification",
                "requirement": "Breach notification procedures",
                "details": "Notify individuals of PHI breaches within 60 days"
            },
            {
                "section": "Access Controls",
                "requirement": "Unique user identification and access controls",
                "details": "Implement procedures for emergency access"
            }
        ]
    },
    "FDA_Software": {
        "title": "FDA Software as a Medical Device (SaMD) Guidance",
        "requirements": [
            {
                "section": "Clinical Validation",
                "requirement": "Clinical validation of software functionality",
                "details": "Demonstrate software performs as intended in clinical setting"
            },
            {
                "section": "Risk Management",
                "requirement": "Risk analysis and management",
                "details": "Identify and mitigate software-related risks"
            },
            {
                "section": "Documentation",
                "requirement": "Software documentation and labeling",
                "details": "Clear instructions for use and technical specifications"
            }
        ]
    },
    "GDPR_Health": {
        "title": "GDPR Health Data Protection",
        "requirements": [
            {
                "section": "Data Minimization",
                "requirement": "Collect only necessary health data",
                "details": "Limit data collection to what's essential for the intended purpose"
            },
            {
                "section": "Consent Management",
                "requirement": "Explicit consent for health data processing",
                "details": "Obtain clear, informed consent for data processing"
            },
            {
                "section": "Data Subject Rights",
                "requirement": "Right to access and delete health data",
                "details": "Provide mechanisms for data access and deletion requests"
            }
        ]
    }
}

def analyze_compliance(application_data, regulation_name):
    """Analyze application compliance against specific regulation"""
    if regulation_name not in REGULATIONS:
        return {"error": "Regulation not found"}
    
    regulation = REGULATIONS[regulation_name]
    app_text = json.dumps(application_data).lower()
    
    compliance_results = []
    
    for req in regulation["requirements"]:
        # Simple keyword-based compliance analysis
        compliance_score = 0
        findings = []
        
        # Check for PHI protection
        if "phi" in req["details"].lower() or "health information" in req["details"].lower():
            if "encryption" in app_text or "hipaa" in app_text or "secure" in app_text:
                compliance_score += 50
                findings.append("Encryption mentioned in infrastructure")
            if "access" in app_text:
                compliance_score += 30
                findings.append("Access controls mentioned")
        
        # Check for technical safeguards
        if "technical" in req["details"].lower() or "security" in req["details"].lower():
            if "aws" in app_text and "hipaa" in app_text:
                compliance_score += 60
                findings.append("HIPAA-compliant cloud infrastructure")
            if "encryption" in app_text:
                compliance_score += 40
                findings.append("Encryption at rest mentioned")
        
        # Check for data management
        if "data" in req["details"].lower():
            if "database" in app_text:
                compliance_score += 30
                findings.append("Database infrastructure specified")
        
        # Check for validation/risk
        if "validation" in req["details"].lower() or "risk" in req["details"].lower():
            if "severity" in app_text or "score" in app_text:
                compliance_score += 40
                findings.append("Scoring system may indicate validation")
        
        # Check for documentation
        if "documentation" in req["details"].lower() or "labeling" in req["details"].lower():
            if "platform" in app_text or "digital" in app_text:
                compliance_score += 20
                findings.append("Digital platform implies documentation")
        
        # Determine compliance level
        if compliance_score >= 70:
            status = "COMPLIANT"
        elif compliance_score >= 40:
            status = "PARTIALLY_COMPLIANT"
        else:
            status = "NON_COMPLIANT"
        
        compliance_results.append({
            "section": req["section"],
            "requirement": req["requirement"],
            "details": req["details"],
            "compliance_score": compliance_score,
            "status": status,
            "findings": findings
        })
    
    return {
        "regulation": regulation_name,
        "regulation_title": regulation["title"],
        "application": application_data,
        "compliance_results": compliance_results
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/regulations')
def get_regulations():
    return jsonify({
        "regulations": [
            {"key": key, "title": reg["title"]} 
            for key, reg in REGULATIONS.items()
        ]
    })

@app.route('/api/analyze', methods=['POST'])
def analyze_application():
    try:
        data = request.get_json()
        application_data = data.get('application', {})
        regulation_name = data.get('regulation', '')
        
        if not application_data or not regulation_name:
            return jsonify({"error": "Missing application data or regulation"})
        
        results = analyze_compliance(application_data, regulation_name)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
