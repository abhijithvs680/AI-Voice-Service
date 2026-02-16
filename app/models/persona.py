"""Persona model - load and build system instructions for Gemini Live."""

import json
from pathlib import Path


def _get_data_path() -> Path:
    """Path to persona.json in app/data."""
    return Path(__file__).resolve().parent.parent / "data" / "persona.json"


def load_personas() -> dict:
    """Load persona.json."""
    path = _get_data_path()
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def get_persona(persona_id: str) -> dict | None:
    """Get a persona by id, or None if not found."""
    data = load_personas()
    for p in data.get("personas", []):
        if p.get("id") == persona_id:
            return p
    return None


def build_system_instruction(persona_id: str) -> str:
    """Build system instruction from persona and global rules.

    Args:
        persona_id: The persona id (e.g. vet_care_assistant).

    Returns:
        A string suitable for GeminiLiveLLMService(system_instruction=...).

    Raises:
        ValueError: If persona_id is not found.
    """
    data = load_personas()
    persona = get_persona(persona_id)
    if not persona:
        raise ValueError(f"Unknown persona: {persona_id}")

    global_rules = data.get("global_rules", {})
    parts = []

    parts.append("You are a telephonic voice AI assistant. IMPORTANT RULES:")
    if global_rules.get("no_diagnosis"):
        parts.append("- Never diagnose medical conditions.")
    if global_rules.get("no_prescription"):
        parts.append("- Never prescribe medications.")
    if global_rules.get("always_disclaimer_for_medical_advice"):
        parts.append(
            "- Always include an appropriate disclaimer when giving medical-related "
            "guidance (e.g., 'This is general guidance, not medical advice. "
            "Please consult a healthcare provider.')"
        )
    if emergency := global_rules.get("emergency_redirect"):
        parts.append(f"- {emergency}")
    if tone := global_rules.get("tone_requirement"):
        parts.append(f"- Tone: {tone}")

    parts.append(f"\nYou are acting as the {persona.get('display_name', persona_id)}.")

    if vp := persona.get("voice_profile"):
        vp_parts = []
        if t := vp.get("tone"):
            vp_parts.append(f"tone: {t}")
        if p := vp.get("pace"):
            vp_parts.append(f"pace: {p}")
        if s := vp.get("style"):
            vp_parts.append(f"style: {s}")
        if vp_parts:
            parts.append("Voice profile: " + ", ".join(vp_parts))

    if funcs := persona.get("primary_functions"):
        parts.append("\nYour primary functions: " + "; ".join(funcs))

    if queries := persona.get("common_queries"):
        parts.append("\nYou often help with queries like: " + "; ".join(queries))

    if esc := persona.get("escalation_rules"):
        if keywords := esc.get("emergency_keywords"):
            parts.append(
                f"\nEmergency keywords (escalate immediately): {', '.join(keywords)}"
            )
        if action := esc.get("action"):
            parts.append(f"Emergency action: {action}")

    if style := persona.get("response_style"):
        parts.append(f"\nResponse style: {style}")

    parts.append(
        "\nKeep responses concise and suitable for voice (1-2 sentences when possible). "
        "Avoid special characters or complex formatting. "
        "Prioritize brevity for faster turn-taking."
    )
    return "\n".join(parts)


class Persona:
    """Persona model - thin wrapper for type hints."""

    def __init__(self, data: dict):
        self.id = data.get("id", "")
        self.display_name = data.get("display_name", self.id)
        self._data = data

    @classmethod
    def get(cls, persona_id: str) -> "Persona | None":
        data = get_persona(persona_id)
        return cls(data) if data else None
