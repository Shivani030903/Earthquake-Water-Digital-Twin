soil_factor = {"rock": 1.0, "clay": 1.4, "sand": 1.6}

def seismic_stress(magnitude, distance, soil):
    return magnitude * soil_factor[soil] / (distance + 1)