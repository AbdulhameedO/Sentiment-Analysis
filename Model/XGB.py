import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


# Implement a simple decision tree
class SimpleDecisionTree:
    def __init__(self, max_depth=3):
        self.max_depth = max_depth
        self.tree = None

    def fit(self, X, y):
        self.tree = self._build_tree(X, y, depth=0)

    def _build_tree(self, X, y, depth):
        if depth >= self.max_depth or len(set(y)) == 1:
            return np.mean(y)
        best_feature, best_threshold = self._best_split(X, y)
        if best_feature is None:
            return np.mean(y)
        left_mask = X[:, best_feature] <= best_threshold
        right_mask = X[:, best_feature] > best_threshold
        left_tree = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_tree = self._build_tree(X[right_mask], y[right_mask], depth + 1)
        return (best_feature, best_threshold, left_tree, right_tree)

    def _best_split(self, X, y):
        best_gain = -np.inf
        best_feature, best_threshold = None, None
        for feature in range(X.shape[1]):
            thresholds = np.unique(X[:, feature])
            for threshold in thresholds:
                gain = self._information_gain(X, y, feature, threshold)
                if gain > best_gain:
                    best_gain, best_feature, best_threshold = gain, feature, threshold
        return best_feature, best_threshold

    def _information_gain(self, X, y, feature, threshold):
        left_mask = X[:, feature] <= threshold
        right_mask = X[:, feature] > threshold
        if len(set(left_mask)) == 1:
            return 0
        left_y, right_y = y[left_mask], y[right_mask]
        p_left, p_right = len(left_y) / len(y), len(right_y) / len(y)
        return self._entropy(y) - p_left * self._entropy(left_y) - p_right * self._entropy(right_y)

    def _entropy(self, y):
        probabilities = [np.mean(y == c) for c in np.unique(y)]
        return -np.sum([p * np.log2(p) for p in probabilities if p > 0])

    def predict(self, X):
        return np.array([self._predict_instance(x, self.tree) for x in X])

    def _predict_instance(self, x, tree):
        if not isinstance(tree, tuple):
            return tree
        feature, threshold, left_tree, right_tree = tree
        if x[feature] <= threshold:
            return self._predict_instance(x, left_tree)
        else:
            return self._predict_instance(x, right_tree)

# Implement gradient boosting
class SimpleXGBoost:
    def __init__(self, n_estimators=10, learning_rate=0.1, max_depth=3):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.models = []

    def fit(self, X, y):
        self.models = []
        y_pred = np.zeros(y.shape)
        for _ in range(self.n_estimators):
            residuals = y - y_pred
            model = SimpleDecisionTree(max_depth=self.max_depth)
            model.fit(X, residuals)
            y_pred += self.learning_rate * model.predict(X)
            self.models.append(model)

    def predict(self, X):
        y_pred = np.zeros(X.shape[0])
        for model in self.models:
            y_pred += self.learning_rate * model.predict(X)
        return np.where(y_pred > 0.5, 1, 0)
