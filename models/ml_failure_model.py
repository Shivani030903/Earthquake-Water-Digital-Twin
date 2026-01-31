import numpy as np
from sklearn.linear_model import LogisticRegression

#Prevents dominance of large-scale features (e.g., length vs soil).

from sklearn.preprocessing import StandardScaler

# Example training data (In real deployment, it would be trained on historical pipe failure records.)
X_train = np.array([
    [0.2, 10, 0.3, 0.2],
    [0.8, 40, 0.8, 0.7],
    [0.6, 30, 0.6, 0.5],
    [0.9, 50, 0.9, 0.8]
])

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)

model = LogisticRegression()

y_train = [0, 1, 1, 1]
model.fit(X_train, y_train)

def predict_failure_probability(stress, age, material, soil):

    """
    Predicts probability of pipe failure.
    Falls back to deterministic rule if ML model is unavailable.
    """

    # ------------------------------------
    # STEP 3: Deterministic fallback
    # ------------------------------------
    if model is None:
        # Simple risk-based estimation
        return min(0.9, stress * 0.3)

    # ------------------------------------
    # ML-based prediction
    # ------------------------------------
    X = scaler.transform([[stress, age, material, soil]])
    return model.predict_proba(X)[0][1]   # Probability of failure