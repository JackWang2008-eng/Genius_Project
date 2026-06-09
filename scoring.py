def calculate_priority(urgency, factors):
    score = 0
    reasons = []


    urgency_points = {
        "Low": 10,
        "Medium": 20,
        "High": 30,
        "Critical": 40
    }


    factor_points = {
        "Elderly": 15,
        "Disabled": 15,
        "Child": 10,
        "Pregnant": 10,
        "No vehicle": 10,
        "Medical condition": 20
    }

    
    urgency_score = urgency_points.get(urgency, 0)
    score += urgency_score
    if urgency_score != 0:
        reasons.append(f"Urgency level '{urgency}' contributes {urgency_score} points.")
    
    for factor in factors:
        factor_score = factor_points.get(factor, 0)
        score += factor_score
        if factor_score != 0:
            reasons.append(f"Factor '{factor}' contributes {factor_score} points.")

    return score, reasons