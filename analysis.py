import json

# This is a very simple "expert rule" for our snakebite scenario
def analyze_snakebite_group(patients):
    """Finds the patient with the fewest bites, as they are often highest risk."""
    if not patients:
        return None
    
    highest_risk_patient = min(patients, key=lambda p: p.get('bite_count', 99))
    return {
        "patient_id": highest_risk_patient['id'],
        "insight_code": "HIGH_RISK_SINGLE_BITE",
        "insight_text": "Prioritize: Single bite victim may have higher venom concentration."
    }

if __name__ == "__main__":
    # In a real system, this would read from a mounted file or stdin
    # For this simulation, we'll use a simple hardcoded example
    mock_input_data = {
        "group_type": "snakebite",
        "patients": [
            {"id": "patient-1", "bite_count": 1},
            {"id": "patient-2", "bite_count": 2},
            {"id": "patient-3", "bite_count": 2}
        ]
    }
    
    result = analyze_snakebite_group(mock_input_data["patients"])
    
    # The script's output is a JSON string
    print(json.dumps(result))