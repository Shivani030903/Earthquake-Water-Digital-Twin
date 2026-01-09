import numpy as np
from sklearn.linear_model import LogisticRegression

model = LogisticRegression()

# Example training data (replace with real later)
X_train = np.array([
    [0.2, 10, 0.3, 0.2],
    [0.8, 40, 0.8, 0.7],
    [0.6, 30, 0.6, 0.5],
    [0.9, 50, 0.9, 0.8]
])
y_train = [0, 1, 1, 1]

model.fit(X_train, y_train)

def predict_failure_probability(stress, age, material, soil):
    X = [[stress, age, material, soil]]
    return model.predict_proba(X)[0][1]   # Probability of failure