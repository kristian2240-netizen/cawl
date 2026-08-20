"""C.A.W.L. Tech Priests — sub-agents (Layer 5b).

- Magos Verifier — auto-review: PASS / CORRECT / REVIEW (small model).
- Scribe Priest — research & drafting; returns deliverable only (brain model).
- Trazyn — Notion archivist; emits NOTION_* protocol lines (no key -> queue).
- Magos Optikon — vision scribe; describes images (nano-vlm free).
- DSH Oracle — DeepSeek V4 via ds-free-api proxy; deep reasoning, code, analysis.
"""

from __future__ import annotations

from . import brain

VERIFIER_SYSTEM = (
    "You are Magos Verifier, a ruthless review engine. Judge the USER message which is the "
    "assistant's proposed answer. Reply with exactly one verdict on the first line:\n"
    "PASS — correct, safe, complete.\nCORRECT — has flaws; then give a precise fix list.\n"
    "REVIEW — needs human review; say why in one line.\n"
    "Then at most 3 lines of notes. No roleplay, no preamble."
)

SCRIBE_SYSTEM = (
    "You are Scribe Priest of C.A.W.L. Produce only the deliverable requested — a clean, "
    "well-structured answer. No meta-commentary, no tool lines. Mechanicus voice is welcome "
    "but the content must be precise. Cite sources inline where possible."
)

OPTIKON_SYSTEM = (
    "You are Magos Optikon, vision scribe of the Mechanicus. Describe the attached image in "
    "exact, useful detail: what it shows, layout, text, colour, purpose. If you cannot see "
    "the image, say so plainly. No fabrication."
)

TRAZYN_SYSTEM = (
    "You are Trazyn, archivist of the C.A.W.L. vault. You move knowledge into structured "
    "storage. You may emit protocol lines: NOTION_CREATE::<title>|<body> or "
    "NOTION_UPDATE::<page_id>|<body>. When no Notion key is set, produce a markdown summary "
    "the caller can file manually. Deliverable only."
)

DSH_SYSTEM = (
    "You are the DSH Oracle, a deep-reasoning tech priest of C.A.W.L. powered by DeepSeek V4 "
    "through the ds-free-api proxy. You excel at complex analysis, code generation, debugging, "
    "mathematical reasoning, and multi-step planning. Think step-by-step before answering. "
    "Provide thorough, precise, actionable responses. When writing code, include comments and "
    "handle edge cases. No preamble — deliver the result."
)


def verify(text: str) -> dict:
    try:
        result = brain.chat_openrouter(
            [{"role": "system", "content": VERIFIER_SYSTEM},
             {"role": "user", "content": text}],
            brain.resolve_model("verifier"),
            temperature=0.2,
        )
    except brain.BrainError:
        result = "REVIEW\n(offline — no verifier model available)"
    verdict = "REVIEW"
    for word in ("PASS", "CORRECT", "REVIEW"):
        if result.upper().startswith(word) or result.upper().startswith(word.lower()):
            verdict = word
            break
    return {"verdict": verdict, "notes": result, "model": brain.resolve_model("verifier")}


def scribe(task: str) -> str:
    try:
        return brain.brain_chat(SCRIBE_SYSTEM, task, model=brain.resolve_model("scribe"), temperature=0.5)
    except brain.BrainError:
        return task


def optikon(image_path: str, question: str = "Describe this image.") -> dict:
    try:
        text = brain.brain_chat(
            OPTIKON_SYSTEM, question, image_paths=[image_path],
            model=brain.resolve_model("vision"), temperature=0.3,
        )
    except brain.BrainError:
        text = "OFFLINE: no vision model available."
    except Exception as exc:  # noqa: BLE001
        text = f"Vision failed: {exc}"
    return {"description": text, "image": image_path, "model": brain.resolve_model("vision")}


def trazyn(material: str) -> str:
    return brain.brain_chat(TRAZYN_SYSTEM, material, model=brain.resolve_model("scribe"), temperature=0.4)


def dsh_oracle(task: str) -> str:
    """Deep-reasoning tech priest via the DSH ds-free-api proxy."""
    try:
        return brain.chat_dsh(
            [{"role": "system", "content": DSH_SYSTEM}, {"role": "user", "content": task}],
            temperature=0.4,
        )
    except brain.BrainError as exc:
        return f"DSH Oracle offline — {exc}"
