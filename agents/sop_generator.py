"""
SOP Generator Agent
Generates a proposed gold-standard SOP based on regulation requirements
and gaps identified in SOP1 and SOP2.
"""

import anthropic

client = None

def get_client():
    global client
    if client is None:
        client = anthropic.Anthropic()
    return client


def generate_proposed_sop(regulation: dict, sop1_gaps: list, sop2_gaps: list) -> dict:
    """
    Generate a proposed compliant SOP based on regulation requirements
    and the gaps found in both SOPs.
    """
    requirements_list = "\n".join(f"- {r}" for r in regulation["key_requirements"])
    gaps1 = "\n".join(f"- {g}" for g in sop1_gaps) if sop1_gaps else "None identified"
    gaps2 = "\n".join(f"- {g}" for g in sop2_gaps) if sop2_gaps else "None identified"

    prompt = f"""You are a regulatory affairs expert specializing in FDA, HIPAA, and GDPR compliance for digital health software.

Based on the following regulation and gaps identified in two existing SOPs, generate a proposed gold-standard SOP that fully addresses all requirements.

REGULATION: {regulation["title"]}

KEY REQUIREMENTS:
{requirements_list}

GAPS FROM SOP 1 (John Doe):
{gaps1}

GAPS FROM SOP 2 (Jane Doe):
{gaps2}

Generate a concise, compliance-focused SOP that:
1. Addresses every key regulation requirement
2. Closes all identified gaps from both SOPs
3. Uses clear, professional language appropriate for a regulated environment
4. Includes these sections: Purpose, Scope, Responsibilities, Procedure, References
5. Keeps steps high-level but specific enough to be actionable
6. Labels this as SOP-PROPOSED with Author: AI Compliance Agent
7. Do NOT use emojis or special symbols

Format in plain text with clear section headers using dashes, not markdown symbols. Keep it practical — this is a demo tool."""

    try:
        response = get_client().messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return {"success": True, "data": response.content[0].text.strip()}

    except anthropic.APIError as e:
        return {"success": False, "error": f"Claude API error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
