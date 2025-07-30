from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import numpy as np

# XOR toy-set
X = np.array([[0,0],[0,1],[1,0],[1,1]])
y = np.array([0,1,1,0])

# CO_DATASCIENTIST_BLOCK_START

pipe = Pipeline([
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
# This makes it a great test for feature engineering or non-linear models.