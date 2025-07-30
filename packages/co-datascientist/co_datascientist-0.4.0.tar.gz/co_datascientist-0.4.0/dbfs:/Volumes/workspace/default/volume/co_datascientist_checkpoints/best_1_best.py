from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

# XOR toy-set
X = np.array([[0,0],[0,1],[1,0],[1,1]])
y = np.array([0,1,1,0])

# CO_DATASCIENTIST_BLOCK_START

class InteractionFeature(BaseEstimator, TransformerMixin):
    """
    Custom transformer to add interaction feature (product of two input features).
    This helps the linear model to represent the non-linear XOR pattern by providing
    a non-linear feature explicitly.
    """
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        interaction = (X[:, 0] * X[:, 1]).reshape(-1, 1)
        return np.hstack([X, interaction])

pipe = Pipeline([
    ("interaction", InteractionFeature()),
    ("scale", StandardScaler()),
    ("clf", LogisticRegression(random_state=0))
])

pipe.fit(X, y)
acc = accuracy_score(y, pipe.predict(X))

# CO_DATASCIENTIST_BLOCK_END


print(f"KPI: {acc:.4f}")  # 🎯 Tag your metric!

# comments
# This is the classic XOR problem — it's not linearly separable!
# A linear model like LogisticRegression can't solve it perfectly,
# because no straight line can separate the classes in 2D.
# By adding the interaction feature (x1 * x2), we create a non-linear basis
# that allows the linear classifier to fit the XOR pattern perfectly.
# This simple, novel feature engineering approach improves accuracy from 0.5 to 1.0.