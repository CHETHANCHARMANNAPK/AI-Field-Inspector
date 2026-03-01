import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.config import (
    OPENAI_API_KEY,
    GOOGLE_API_KEY,
    LLM_PROVIDER,
)

SYSTEM_PROMPT = """You are an expert infrastructure inspection engineer working for a large equipment manufacturer.

Given a list of detected damages (each with type, confidence score, severity, and bounding-box location), generate a **professional inspection report** in valid JSON with the following structure:

{
  "summary": "A 2-3 sentence executive summary of the inspection findings.",
  "overall_risk_level": "critical | high | medium | low",
  "findings": [
    {
      "id": 1,
      "damage_type": "crack",
      "severity": "high",
      "confidence": 0.87,
      "location_description": "Upper-left quadrant of the structure",
      "explanation": "A significant crack was detected, which may indicate underlying structural stress.",
      "recommended_action": "Schedule immediate structural engineering review."
    }
  ],
  "safety_notes": [
    "Restrict access to the affected area until inspection is complete.",
    "Wear appropriate PPE when approaching corrosion sites."
  ],
  "checklist": [
    {"item": "Visual verification of crack #1", "status": "pending"},
    {"item": "Corrosion depth measurement", "status": "pending"},
    {"item": "Leak source identification", "status": "pending"},
    {"item": "Structural load assessment", "status": "pending"}
  ],
  "responsible_ai_note": "This report is AI-generated to assist human inspectors. All findings should be validated by a qualified professional before any action is taken. AI assists — it does not replace — expert judgment."
}

Rules:
- Be specific and actionable.
- Always include the responsible AI note exactly as shown.
- overall_risk_level should be the HIGHEST severity among all findings.
- Return ONLY valid JSON, no markdown fences, no extra text.
"""


def _build_user_prompt(detections: List[Dict[str, Any]], image_name: str) -> str:
    det_text = json.dumps(detections, indent=2)
    return (
        f"Inspection Image: {image_name}\n"
        f"Inspection Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        f"Detected damages:\n{det_text}\n\n"
        "Generate the inspection report JSON."
    )


def _generate_with_openai(user_prompt: str) -> Dict[str, Any]:
    from openai import OpenAI

    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )
    return json.loads(response.choices[0].message.content)


def _generate_with_gemini(user_prompt: str) -> Dict[str, Any]:
    from google import genai

    client = genai.Client(api_key=GOOGLE_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"{SYSTEM_PROMPT}\n\n{user_prompt}",
        config={
            "temperature": 0.3,
            "response_mime_type": "application/json",
        },
    )
    return json.loads(response.text)


def _generate_fallback(detections: List[Dict[str, Any]], image_name: str) -> Dict[str, Any]:
    highest = "low"
    severity_rank = {"low": 0, "medium": 1, "high": 2, "critical": 3}

    findings = []
    checklist = []
    for i, d in enumerate(detections, 1):
        sev = d.get("severity", "medium")
        if severity_rank.get(sev, 0) > severity_rank.get(highest, 0):
            highest = sev

        findings.append({
            "id": i,
            "damage_type": d["type"],
            "severity": sev,
            "confidence": d["confidence"],
            "location_description": f"Region at pixel ({d['bbox']['x']}, {d['bbox']['y']})",
            "explanation": d.get("description", f"{d['type']} detected."),
            "recommended_action": _action_for(d["type"], sev),
        })
        checklist.append({
            "item": f"Verify {d['type']} finding #{i}",
            "status": "pending",
        })

    count = len(detections)
    type_set = list({d["type"] for d in detections})
    summary = (
        f"Inspection of {image_name} revealed {count} potential issue(s) "
        f"including {', '.join(type_set)}. "
        f"Overall risk is assessed as {highest.upper()}. Immediate human review is recommended."
    )

    return {
        "summary": summary,
        "overall_risk_level": highest,
        "findings": findings,
        "safety_notes": [
            "Restrict access to the affected area until inspection is complete.",
            "Wear appropriate PPE when approaching corrosion or leak sites.",
            "Do not operate heavy machinery near identified damage zones.",
            "Ensure all findings are reviewed by a certified structural engineer.",
        ],
        "checklist": checklist,
        "responsible_ai_note": (
            "This report is AI-generated to assist human inspectors. "
            "All findings should be validated by a qualified professional "
            "before any action is taken. AI assists — it does not replace — expert judgment."
        ),
    }


def _action_for(damage_type: str, severity: str) -> str:
    actions = {
        "crack": {
            "critical": "Immediately halt operations and schedule emergency structural assessment.",
            "high": "Schedule urgent structural engineering review within 24 hours.",
            "medium": "Monitor crack progression; schedule inspection within 1 week.",
            "low": "Document and include in routine maintenance schedule.",
        },
        "corrosion": {
            "critical": "Replace affected component immediately; risk of structural failure.",
            "high": "Apply corrosion treatment and schedule replacement within 48 hours.",
            "medium": "Apply protective coating; re-inspect in 2 weeks.",
            "low": "Note in maintenance log; monitor during next scheduled inspection.",
        },
        "leak": {
            "critical": "Shut down system immediately; isolate leak source.",
            "high": "Reduce system pressure and schedule emergency repair.",
            "medium": "Monitor leak rate; schedule repair within 1 week.",
            "low": "Document location; include in preventive maintenance.",
        },
        "misalignment": {
            "critical": "Stop equipment operation; realign before restarting.",
            "high": "Schedule realignment within 24 hours.",
            "medium": "Monitor vibration levels; schedule correction within 1 week.",
            "low": "Note in maintenance log; correct during next scheduled downtime.",
        },
    }
    return actions.get(damage_type, actions["crack"]).get(severity, "Schedule inspection.")


def generate_report(
    detections: List[Dict[str, Any]],
    image_name: str = "uploaded_image.jpg",
) -> Dict[str, Any]:
    user_prompt = _build_user_prompt(detections, image_name)

    try:
        if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
            return _generate_with_openai(user_prompt)
        elif LLM_PROVIDER == "gemini" and GOOGLE_API_KEY:
            return _generate_with_gemini(user_prompt)
    except Exception as e:
        print(f"[report_generator] LLM call failed ({e}); using fallback.")

    return _generate_fallback(detections, image_name)
