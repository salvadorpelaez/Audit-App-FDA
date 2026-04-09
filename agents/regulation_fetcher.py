"""
Regulation Fetcher Agent
Pulls live regulation text from eCFR API for 21 CFR sections.
HIPAA and GDPR use curated full-text (no public live API exists for these).
"""

import requests

ECFR_BASE = "https://www.ecfr.gov/api/versioner/v1"
ECFR_DATE = "2024-01-01"


def fetch_ecfr_part(title: int, part: int) -> str:
    """Fetch regulation text for a specific CFR title/part from eCFR API."""
    url = f"{ECFR_BASE}/full/{ECFR_DATE}/title-{title}.xml"
    params = {"part": str(part)}
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            # Strip XML tags to get plain text for Claude
            import re
            text = re.sub(r'<[^>]+>', ' ', response.text)
            text = re.sub(r'\s+', ' ', text).strip()
            # Cap at ~8000 chars to keep tokens manageable
            return text[:8000]
        else:
            return None
    except requests.RequestException:
        return None


def get_regulation_text(regulation_key: str) -> dict:
    """
    Returns regulation text and metadata for a given regulation key.
    For 21 CFR sections: fetches live from eCFR.
    For HIPAA/GDPR: returns curated full-text.
    """

    if regulation_key == "21_CFR_880":
        live_text = fetch_ecfr_part(21, 880)
        return {
            "title": "21 CFR Part 880 — General Hospital and Personal Use Devices",
            "source": "Live — eCFR API (ecfr.gov)",
            "live": True,
            "text": live_text or FALLBACK_21_CFR_880,
            "key_requirements": [
                "Device Classification (Class I, II, or III based on risk level)",
                "Regulatory Controls (General Controls / Special Controls / PMA)",
                "Premarket Notification (510(k)) requirements",
                "Quality System Regulation compliance",
                "Clear intended use and device definition",
                "Applicable exemptions identified"
            ]
        }

    elif regulation_key == "FDA_Software":
        live_text = fetch_ecfr_part(21, 820)
        return {
            "title": "FDA Software as a Medical Device (SaMD) — 21 CFR Part 820 + FDA Guidance",
            "source": "Live 21 CFR Part 820 — eCFR API + FDA SaMD Guidance (curated)",
            "live": True,
            "text": (live_text or FALLBACK_FDA_SAMD) + "\n\n" + FDA_SAMD_GUIDANCE,
            "key_requirements": [
                "Clinical validation of software functionality",
                "Risk classification (significance of information provided by SaMD)",
                "Software lifecycle documentation",
                "Cybersecurity considerations",
                "Intended use clearly defined and limited to stated purpose",
                "Design controls and change management"
            ]
        }

    elif regulation_key == "HIPAA":
        return {
            "title": "HIPAA — Health Insurance Portability and Accountability Act",
            "source": "Curated — no live public API exists for HIPAA regulation text",
            "live": False,
            "text": HIPAA_TEXT,
            "key_requirements": [
                "Protected Health Information (PHI) safeguards",
                "Administrative, physical, and technical safeguards",
                "Breach notification within 60 days",
                "Unique user identification and access controls",
                "Audit controls and integrity controls",
                "Business Associate Agreements (BAA) where applicable"
            ]
        }

    elif regulation_key == "GDPR_Health":
        return {
            "title": "GDPR — Health Data Protection (Article 9)",
            "source": "Curated — EUR-Lex API does not provide structured health data provisions",
            "live": False,
            "text": GDPR_TEXT,
            "key_requirements": [
                "Explicit consent for processing special category (health) data",
                "Data minimization — collect only what is necessary",
                "Right of access and right to erasure",
                "Data Protection Impact Assessment (DPIA) for high-risk processing",
                "Data Protection Officer (DPO) designation if required",
                "Cross-border transfer restrictions"
            ]
        }

    return None


# --- Fallback and curated regulation texts ---

FALLBACK_21_CFR_880 = """
21 CFR Part 880 — General Hospital and Personal Use Devices

Subpart A — General Provisions
880.1 Scope. This part sets forth the classification of general hospital and personal use devices.

Subpart B — General Hospital and Personal Use Diagnostic Devices
Devices must be classified as Class I (General Controls), Class II (Special Controls),
or Class III (Premarket Approval) based on the level of risk to patients.

Class I devices are subject to General Controls only (labeling, registration,
adverse event reporting). Many Class I devices are exempt from 510(k) premarket notification.

Class II devices require Special Controls in addition to General Controls.
Special controls may include performance standards, postmarket surveillance,
patient registries, special labeling, premarket data requirements, and guidelines.

Class III devices require Premarket Approval (PMA) — the most stringent pathway,
requiring valid scientific evidence of safety and effectiveness.

880.9 Limitations of exemptions. Exemptions do not apply to devices that are
intended for a use different from the intended use of a legally marketed device.
"""

FALLBACK_FDA_SAMD = """
21 CFR Part 820 — Quality System Regulation

820.30 Design controls. Manufacturers of devices shall establish and maintain
procedures to control the design of the device in order to ensure that specified
design requirements are met.

820.30(g) Design validation. Manufacturers shall establish and maintain procedures
for validating the device design. Design validation shall be performed under defined
operating conditions on initial production units, lots, or batches, or their equivalents.

820.70 Production and process controls. Manufacturers shall develop, conduct, control,
and monitor production processes to ensure that a device conforms to its specifications.

820.100 Corrective and preventive action. Manufacturers shall establish and maintain
procedures for implementing corrective and preventive action.
"""

FDA_SAMD_GUIDANCE = """
FDA Software as a Medical Device (SaMD) Guidance — Key Principles

SaMD is defined as software intended to be used for medical purposes that performs
these purposes without being part of a hardware medical device.

Risk Classification Framework (based on IMDRF):
- Category I: Non-serious situations, treat or diagnose non-serious conditions
- Category II: Serious situations, treat or diagnose non-serious conditions
- Category III: Non-serious situations, treat or diagnose serious conditions
- Category IV: Serious or critical situations — highest risk, most stringent requirements

Key requirements for SaMD:
1. Clearly defined intended use — the software must do what it claims
2. Clinical validation — evidence the software performs as intended in real-world use
3. Cybersecurity — must address cybersecurity risks throughout the lifecycle
4. Real-world performance monitoring — post-market surveillance
5. Algorithm transparency — AI/ML-based SaMD must address algorithm change protocols
"""

HIPAA_TEXT = """
HIPAA Privacy Rule (45 CFR Parts 160 and 164)

The Privacy Rule establishes national standards to protect individuals' medical records
and other individually identifiable health information (collectively defined as
"protected health information" or PHI).

Key requirements:
- PHI must not be used or disclosed except as the Privacy Rule permits or requires
- Covered entities must provide individuals with notice of their privacy practices
- Individuals have rights to examine and obtain copies of their PHI
- Covered entities must implement appropriate administrative, technical, and physical
  safeguards to protect the privacy of PHI

HIPAA Security Rule (45 CFR Part 164, Subparts A and C)

The Security Rule establishes national standards to protect individuals' electronic
personal health information (ePHI).

Administrative Safeguards:
- Security management process including risk analysis and risk management
- Assigned security responsibility
- Workforce training and management
- Evaluation procedures

Physical Safeguards:
- Facility access controls
- Workstation and device security

Technical Safeguards:
- Access controls — unique user identification, emergency access procedures
- Audit controls — hardware, software, and procedural mechanisms to record activity
- Integrity controls — protect ePHI from improper alteration or destruction
- Transmission security — encryption of ePHI in transit

Breach Notification Rule:
- Covered entities must notify affected individuals within 60 days of discovery
- Breaches affecting 500+ individuals require notification to HHS and media
- Business Associates must notify covered entities within 60 days

Business Associate Agreements (BAA):
- Required when PHI is shared with third-party vendors
- Cloud providers, analytics platforms, and SaaS tools processing PHI require BAAs
"""

GDPR_TEXT = """
GDPR — Regulation (EU) 2016/679 — Health Data Provisions

Article 9 — Processing of special categories of personal data
Health data is classified as a special category requiring explicit consent or
another Article 9(2) legal basis. Processing is prohibited unless:
- Explicit consent has been obtained
- Processing is necessary for preventive or occupational medicine
- Processing is necessary for reasons of public health

Key Principles (Article 5):
- Lawfulness, fairness, and transparency
- Purpose limitation — collected for specified, explicit, legitimate purposes
- Data minimisation — adequate, relevant, limited to what is necessary
- Accuracy — kept accurate and up to date
- Storage limitation — not kept longer than necessary
- Integrity and confidentiality — appropriate security

Individual Rights:
- Right of access (Article 15) — individuals can request their data
- Right to rectification (Article 16)
- Right to erasure / right to be forgotten (Article 17)
- Right to data portability (Article 20)
- Right to object (Article 21)

Data Protection Impact Assessment (DPIA — Article 35):
Required when processing is likely to result in a high risk to individuals.
Health data processing at scale almost always requires a DPIA.

Data Protection Officer (DPO — Article 37):
Required for public authorities and organizations processing health data at large scale.

Cross-border transfers (Chapter V):
Health data may only be transferred outside the EU/EEA to countries with adequate
protection or under appropriate safeguards (Standard Contractual Clauses, etc.).
"""
