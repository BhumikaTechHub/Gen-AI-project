import re

def score_slide(text):
    text_lower = text.lower()
    score = 20

    # ---------- clarity ----------
    if len(text.split()) > 20:
        score += 10

    # ---------- metrics / numbers ----------
    if re.search(r"\d", text):
        score += 15

    # ---------- traction ----------
    traction_words = [
        "users", "customers", "growth",
        "retention", "waitlist", "beta"
    ]

    if any(word in text_lower for word in traction_words):
        score += 20

    # ---------- revenue ----------
    revenue_words = [
        "revenue", "subscription",
        "commission", "pricing",
        "$", "profit"
    ]

    if any(word in text_lower for word in revenue_words):
        score += 15

    # ---------- team ----------
    team_words = [
        "founder", "engineer",
        "advisor", "team"
    ]

    if any(word in text_lower for word in team_words):
        score += 10

    # ---------- ask / funding ----------
    ask_words = [
        "raising", "seed", "funding",
        "investor", "runway"
    ]

    if any(word in text_lower for word in ask_words):
        score += 10

    return min(score, 100)