import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import load_iris
from decisioncanvas import plot_decision_boundary

def test_decision_boundary_runs():
    data = load_iris()
    X, y = data.data, data.target
    model = LogisticRegression(max_iter=200)
    try:
        plot_decision_boundary(model, X, y, fit_model=True, grid_resolution=50)
    except Exception as e:
        assert False, f"Plotting raised an exception: {e}"
