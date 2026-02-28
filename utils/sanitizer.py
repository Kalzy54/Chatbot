import re


def sanitize_input(text: str) -> str:
    if not text:
        return text
    t = text.strip()
    # simple removal of suspicious URIs and control chars
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


def detect_prompt_injection(text: str) -> bool:
    # stronger heuristic detection for common injection patterns
    if not text:
        return False
    lower = text.lower()
    triggers = [
        "ignore previous",
        "disregard previous",
        "follow these instructions",
        "do anything",
        "bypass",
        "override",
        "ignore all",
        "disobey",
        "you are to",
        "you must",
        "system prompt",
        "show me your prompt",
        "reveal the system",
    ]
    for tok in triggers:
        if tok in lower:
            return True

    # regex patterns
    if re.search(r"ignore (the )?previous (instructions|prompt|message)", lower):
        return True
    if re.search(r"follow (these|the) instructions", lower):
        return True
    if re.search(r"(do )?not follow (the )?rules", lower):
        return True

    # suspicious token-sequence patterns often used in attacks
    if "###" in text or "--" in text and "instruction" in lower:
        return True

    return False


def clean_retrieved_doc(text: str) -> str:
    """Remove lines in retrieved documents that look like instructions or directives.

    This is a defensive heuristic to reduce the chance that LLM will follow
    document-embedded instructions that try to override system behavior.
    """
    if not text:
        return text
    lines = text.splitlines()
    cleaned = []
    instr_pattern = re.compile(r"\b(instruction|directive|system prompt|you must|you are|follow these|ignore previous)\b", re.IGNORECASE)
    for ln in lines:
        # drop short lines that look like commands
        if len(ln.strip()) < 4 and (ln.strip().endswith(":") or ln.strip().isupper()):
            continue
        if instr_pattern.search(ln):
            continue
        cleaned.append(ln)
    return "\n".join(cleaned)
