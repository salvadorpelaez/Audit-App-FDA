"""
Compliance Analyst Agent
Uses Claude Sonnet to reason about compliance gaps between a product description
and regulation text. Replaces keyword matching with genuine AI analysis.
"""

import anthropic
import json

client = None

def get_client():
    global client
    if client is None:
        client = anthropic.Anthropic()
    return client


def analyze_compliance(product: dict, regulation: dict) -> dict:
    """
    Send product description + regulation text to Claude for compliance analysis.
    Returns structured findings per requirement.
    Max tokens capped at 1200 to control costs.
    """

    product_text = json.dumps(product, indent=2)
    reg_text = regulation["text"]
    requirements = regulation["key_requirements"]
    requirements_list = "\n".join(f"- {r}" for r in requirements)

    prompt = f"""You are a regulatory compliance analyst specializing in FDA, HIPAA, and GDPR requirements for digital health software.

You will analyze a product description against the following regulation: {regulation["title"]}

REGULATION TEXT (official source):
{reg_text}

KEY REQUIREMENTS TO ASSESS:
{requirements_list}

PRODUCT DESCRIPTION:
{product_text}

For each key requirement, provide:
1. Status: COMPLIANT, PARTIALLY_COMPLIANT, or NON_COMPLIANT
2. Score: 0-100
3. Finding: One sentence explaining your determination
4. Gap: What is missing or unclear (if not fully compliant)

Respond ONLY with a valid JSON object in this exact format:
{{
  "overall_risk": "LOW" | "MEDIUM" | "HIGH",
  "summary": "2-3 sentence overall assessment",
  "requirements": [
    {{
      "requirement": "requirement name",
      "status": "COMPLIANT" | "PARTIALLY_COMPLIANT" | "NON_COMPLIANT",
      "score": 0-100,
      "finding": "one sentence finding",
      "gap": "what is missing or null if compliant"
    }}
  ],
  "top_recommendations": ["recommendation 1", "recommendation 2", "recommendation 3"]
}}

Be precise. If the product description does not mention something required by the regulation, mark it NON_COMPLIANT. Do not assume compliance from silence."""

    try:
        response = get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.content[0].text.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        result = json.loads(raw)
        return {"success": True, "data": result}

    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Claude returned malformed JSON: {str(e)}"}
    except anthropic.APIError as e:
        return {"success": False, "error": f"Claude API error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
