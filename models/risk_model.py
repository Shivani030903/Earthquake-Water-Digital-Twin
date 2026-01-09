material_score = {"CI": 0.9, "DI": 0.6, "PVC": 0.3}
soil_score = {"rock": 0.3, "clay": 0.7, "sand": 0.9}

def compute_risk(stress, age, material, soil):
    return (
        0.35 * stress +
        0.25 * (age / 50) +
        0.2 * material_score[material] +
        0.2 * soil_score[soil]
    )