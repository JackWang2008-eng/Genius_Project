def calculate_triage_score(
    red_flags,
    injury_level,
    mobility_status,
    vulnerable_person,
    evacuation_need,
    safe_shelter,
):
    score = 0
    reasons = []

    red_flag_labels = {
        "trouble_breathing": "Trouble breathing",
        "unconscious_or_confused": "Unconscious or confused",
        "severe_bleeding": "Severe bleeding",
        "chest_pain_or_stroke": "Chest pain or stroke signs",
        "severe_burn": "Severe burn",
    }

    if red_flags: # If there are any red flags, assign critical urgency immediately
        for flag in red_flags:
            label = red_flag_labels.get(flag, flag)
            reasons.append(f"Emergency warning sign: {label}.")
        return "Critical", 100, reasons


    injury_points = {
        "None": 0,
        "Minor": 10,
        "Moderate": 25,
        "Serious": 45,
    }

    mobility_points = {
        "Can walk": 0,
        "Needs help walking": 15,
        "Cannot walk": 30,
    }

    vulnerable_points = {
        "No": 0,
        "Yes": 15,
    }

    evacuation_points = {
        "No": 0,
        "Yes": 20,
    }

    shelter_points = {
        "Yes": 0,
        "No": 20,
    }

    score += injury_points.get(injury_level, 0)
    score += mobility_points.get(mobility_status, 0)
    score += vulnerable_points.get(vulnerable_person, 0)
    score += evacuation_points.get(evacuation_need, 0)
    score += shelter_points.get(safe_shelter, 0)

    if injury_level != "None":
        reasons.append(f"Injury level is {injury_level}.")

    if mobility_status != "Can walk":
        reasons.append(f"Mobility status: {mobility_status}.")

    if vulnerable_person == "Yes":
        reasons.append(
            "Child, elderly, disabled, pregnant, or medically fragile person involved."
        )

    if evacuation_need == "Yes":
        reasons.append("Evacuation support is needed.")

    if safe_shelter == "No":
        reasons.append("No safe shelter is available.")

    score = min(score, 100)

    if score >= 75:
        urgency = "Critical"
    elif score >= 50:
        urgency = "High"
    elif score >= 25:
        urgency = "Medium"
    else:
        urgency = "Low"

    return urgency, score, reasons
