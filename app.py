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
    },
    "21_CFR_880": {
        "title": "21 CFR Part 880 - General Hospital, Personal Use, and Miscellaneous Devices",
        "requirements": [
            {
                "section": "Device Classification",
                "requirement": "Proper classification of medical devices",
                "details": "Devices must be classified as Class I, II, or III based on risk"
            },
            {
                "section": "Regulatory Controls",
                "requirement": "Appropriate controls based on classification",
                "details": "General Controls for Class I, Special Controls for Class II, PMA for Class III"
            },
            {
                "section": "Exemptions",
                "requirement": "Identify applicable exemptions",
                "details": "Some devices may be exempt from premarket notification or QSR requirements"
            },
            {
                "section": "Device Definition",
                "requirement": "Clear device definition and intended use",
                "details": "Device must meet specific definition and intended use criteria"
            }
        ]
    }
}

# Additional regulatory data for 21 CFR 880 devices
FDA_DEVICES = {
    "regulations": [
        {
            "id": "21-CFR-880.5075",
            "name": "Elastic Bandage",
            "classification": "Class I",
            "controls": "General Controls",
            "exemptions": ["Premarket Notification (510k)", "Quality System Regulation (Part 820)"],
            "limitations_reference": "880.9",
            "full_text": "An elastic bandage is a device consisting of either a long flat strip or a tube of elasticized material that is used to support and compress a part of a patient's body."
        },
        {
            "id": "21-CFR-880.5725",
            "name": "Infusion Pump",
            "classification": "Class II",
            "controls": "Special Controls",
            "exemptions": [],
            "full_text": "A device used to decide the amount of fluid to be delivered to a patient and to deliver the fluid under positive pressure."
        }
    ]
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
        
        # Check for device classification (21 CFR 880 specific)
        if regulation_name == "21_CFR_880":
            if "classification" in req["details"].lower():
                if "medical" in app_text or "device" in app_text:
                    compliance_score += 40
                    findings.append("Medical device classification identified")
                if "class i" in app_text or "class ii" in app_text or "class iii" in app_text:
                    compliance_score += 30
                    findings.append("Device class specified")
            
            # Check for regulatory controls
            if "controls" in req["details"].lower():
                if "controls" in app_text or "quality" in app_text:
                    compliance_score += 35
                    findings.append("Regulatory controls mentioned")
            
            # Check for exemptions
            if "exemptions" in req["details"].lower():
                if "exempt" in app_text or "510k" in app_text:
                    compliance_score += 25
                    findings.append("Exemptions considered")
            
            # Check for device definition
            if "definition" in req["details"].lower():
                if "intended use" in app_text or "purpose" in app_text:
                    compliance_score += 30
                    findings.append("Device definition and intended use specified")
        
        # Check for PHI protection (HIPAA specific)
        if regulation_name == "HIPAA":
            if "phi" in req["details"].lower() or "health information" in req["details"].lower():
                if "encryption" in app_text or "hipaa" in app_text or "secure" in app_text:
                    compliance_score += 50
                    findings.append("Encryption mentioned in infrastructure")
                if "access" in app_text:
                    compliance_score += 30
                    findings.append("Access controls mentioned")
        
        # Check for technical safeguards (HIPAA/FDA specific)
        if "technical" in req["details"].lower() or "security" in req["details"].lower():
            if "aws" in app_text and "hipaa" in app_text:
                compliance_score += 60
                findings.append("HIPAA-compliant cloud infrastructure")
            if "encryption" in app_text:
                compliance_score += 40
                findings.append("Encryption at rest mentioned")
        
        # Check for data management (General)
        if "data" in req["details"].lower():
            if "database" in app_text:
                compliance_score += 30
                findings.append("Database infrastructure specified")
        
        # Check for validation/risk (FDA Software specific)
        if regulation_name == "FDA_Software":
            if "validation" in req["details"].lower() or "risk" in req["details"].lower():
                if "severity" in app_text or "score" in app_text:
                    compliance_score += 40
                    findings.append("Scoring system may indicate validation")
        
        # Check for documentation (FDA Software specific)
        if regulation_name == "FDA_Software":
            if "documentation" in req["details"].lower() or "labeling" in req["details"].lower():
                if "platform" in app_text or "digital" in app_text:
                    compliance_score += 20
                    findings.append("Digital platform implies documentation")
        
        # Check for consent and data rights (GDPR specific)
        if regulation_name == "GDPR_Health":
            if "consent" in req["details"].lower():
                if "consent" in app_text or "permission" in app_text:
                    compliance_score += 45
                    findings.append("Consent mechanisms mentioned")
            if "access" in req["details"].lower() and "delete" in req["details"].lower():
                if "export" in app_text or "delete" in app_text:
                    compliance_score += 35
                    findings.append("Data access/deletion capabilities")
        
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

@app.route('/api/fda-devices')
def get_fda_devices():
    """Get FDA device classifications"""
    return jsonify(FDA_DEVICES)

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
