from __future__ import annotations

GENERIC_ANALYZE_PROMPT = (
    "Analyze this image in detail. Describe what you see, including objects, text, layout, and notable details."
)


GENERIC_ANALYZE_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "summary": {"type": "string"},
        "detected_text": {"type": "array", "items": {"type": "string"}},
        "key_elements": {"type": "array", "items": {"type": "string"}},
        "notable_details": {"type": "array", "items": {"type": "string"}},
        "confidence_notes": {"type": "string"},
    },
    "required": [
        "summary",
        "detected_text",
        "key_elements",
        "notable_details",
        "confidence_notes",
    ],
}


WEBPAGE_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "page_title": {"type": "string"},
        "visible_url": {"type": "string"},
        "layout": {"type": "string"},
        "content": {"type": "string"},
        "interactive_elements": {"type": "array", "items": {"type": "string"}},
        "design": {"type": "string"},
        "accessibility": {"type": "string"},
        "usability": {"type": "string"},
        "technical_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "page_title",
        "visible_url",
        "layout",
        "content",
        "interactive_elements",
        "design",
        "accessibility",
        "usability",
        "technical_notes",
    ],
}


MOBILE_JSON_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "app_name": {"type": "string"},
        "platform": {"type": "string"},
        "screen_type": {"type": "string"},
        "ui_design": {"type": "string"},
        "navigation": {"type": "string"},
        "content": {"type": "string"},
        "interactions": {"type": "array", "items": {"type": "string"}},
        "platform_guidelines": {"type": "string"},
        "accessibility": {"type": "string"},
        "ux_heuristics": {"type": "string"},
        "usability": {"type": "string"},
        "technical_notes": {"type": "array", "items": {"type": "string"}},
    },
    "required": [
        "app_name",
        "platform",
        "screen_type",
        "ui_design",
        "navigation",
        "content",
        "interactions",
        "platform_guidelines",
        "accessibility",
        "ux_heuristics",
        "usability",
        "technical_notes",
    ],
}


def build_analyze_prompt(user_prompt: str | None) -> str:
    if not user_prompt:
        return GENERIC_ANALYZE_PROMPT
    return user_prompt


def build_webpage_prompt(
    *,
    focus: str | None,
    include_accessibility: bool,
    user_prompt: str | None,
) -> str:
    lines = [
        "Analyze this webpage screenshot.",
        "Describe the visible layout, content hierarchy, interactive elements, design quality, usability, and technical observations.",
    ]
    if focus:
        lines.append(f"Prioritize this focus area: {focus}.")
    if include_accessibility:
        lines.append("Include accessibility observations such as contrast, semantics, focus cues, and readability.")
    if user_prompt:
        lines.append(f"Additional request: {user_prompt}")
    return "\n".join(lines)


def build_mobile_prompt(
    *,
    platform: str,
    focus: str | None,
    include_ux_heuristics: bool,
    user_prompt: str | None,
) -> str:
    lines = [
        "Analyze this mobile app screenshot.",
        f"Platform expectation: {platform}.",
        "Review the UI design, user experience, navigation, content clarity, accessibility, and implementation-related observations.",
    ]
    if focus:
        lines.append(f"Prioritize this focus area: {focus}.")
    if include_ux_heuristics:
        lines.append("Include UX heuristic feedback where the screenshot provides enough evidence.")
    if user_prompt:
        lines.append(f"Additional request: {user_prompt}")
    return "\n".join(lines)
