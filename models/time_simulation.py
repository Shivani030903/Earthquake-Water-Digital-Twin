def temporal_stress(base_stress, time_min):
    """
    Stress accumulation over time
    """
    return base_stress * (1 + 0.08 * time_min)