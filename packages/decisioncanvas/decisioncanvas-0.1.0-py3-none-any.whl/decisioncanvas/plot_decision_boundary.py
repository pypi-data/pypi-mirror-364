import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from matplotlib.colors import ListedColormap
import matplotlib.cm as cm

def plot_decision_boundary(
    model, X, y,
    class_names=None,
    standardize=True,
    pca_components=2,
    grid_resolution=300,
    padding=1.0,
    cmap_light=None,
    cmap_bold=None,
    alpha=0.3,
    title="Decision Boundary",
    fit_model=True,
    figsize=(8,6),
    random_state=None
):
    """
    Plot decision boundaries for classification models.
    """
    # Validate input
    X = np.asarray(X)
    y = np.asarray(y)
    if len(X) != len(y):
        raise ValueError(f"X and y sample size mismatch: {len(X)} != {len(y)}")
    if X.shape[0] < 2:
        raise ValueError("At least two samples are required for plotting.")
    if len(np.unique(y)) < 2:
        raise ValueError("At least two classes are required for plotting.")

    # Standardize
    if standardize:
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = X.copy()

    # PCA
    n_features = X_scaled.shape[1]
    if n_features > 2:
        pca = PCA(n_components=2, random_state=random_state)
        X_reduced = pca.fit_transform(X_scaled)
        evr = sum(pca.explained_variance_ratio_) * 100
        print(f"PCA reduced data from {n_features} to 2 dims; explained variance: {evr:.2f}%")
    elif n_features == 2:
        X_reduced = X_scaled
    else:
        raise ValueError("Input data must have at least 2 features.")

    # Fit model
    if fit_model:
        model.fit(X_reduced, y)

    # Grid
    x_min, x_max = X_reduced[:, 0].min() - padding, X_reduced[:, 0].max() + padding
    y_min, y_max = X_reduced[:, 1].min() - padding, X_reduced[:, 1].max() + padding
    xx, yy = np.meshgrid(
        np.linspace(x_min, x_max, grid_resolution),
        np.linspace(y_min, y_max, grid_resolution)
    )
    grid_points = np.c_[xx.ravel(), yy.ravel()]

    try:
        Z = model.predict(grid_points)
    except Exception as e:
        raise RuntimeError(f"Model prediction failed on grid points: {e}")
    Z = Z.reshape(xx.shape)

    # Colors
    classes = np.unique(y)
    n_classes = len(classes)
    if class_names is None:
        class_names = {label: str(label) for label in classes}
    elif isinstance(class_names, list):
        class_names = {label: name for label, name in zip(classes, class_names)}
    elif isinstance(class_names, dict):
        pass
    else:
        raise TypeError("class_names must be None, list, or dict")

    if cmap_light is None:
        base_cmap = cm.get_cmap('Pastel1', n_classes)
        cmap_light = ListedColormap(base_cmap.colors[:n_classes])
    if cmap_bold is None:
        base_cmap = cm.get_cmap('Set1', n_classes)
        cmap_bold = base_cmap.colors[:n_classes]

    # Plot
    plt.figure(figsize=figsize)
    plt.contourf(xx, yy, Z, alpha=alpha, cmap=cmap_light)
    for idx, class_val in enumerate(classes):
        mask = (y == class_val)
        plt.scatter(
            X_reduced[mask, 0],
            X_reduced[mask, 1],
            c=[cmap_bold[idx]],
            label=class_names.get(class_val, class_val),
            edgecolor='k',
            s=40
        )
    plt.xlabel("Feature 1 (PCA)" if n_features > 2 else "Feature 1 (Standardized)")
    plt.ylabel("Feature 2 (PCA)" if n_features > 2 else "Feature 2 (Standardized)")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()
