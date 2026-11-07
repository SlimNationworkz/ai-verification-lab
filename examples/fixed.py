"""Correct implementation of the independent example specification."""

def unique_usernames(names):
    seen = set()
    result = []
    for name in names:
        cleaned = name.strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result
