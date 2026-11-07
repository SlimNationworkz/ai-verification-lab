"""Intentional training example: wrong case-insensitive deduplication + blank handling."""

def unique_usernames(names):
    seen = set()
    result = []
    for name in names:
        cleaned = name.strip()
        if cleaned.lower() not in seen:
            result.append(cleaned)
            seen.add(cleaned)  # BUG: should add cleaned.lower()
    return result  # BUG: also retains blank entries
