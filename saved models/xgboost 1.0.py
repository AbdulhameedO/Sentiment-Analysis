import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, accuracy_score

class DecisionTree:
    def __init__(self, max_depth=3, min_samples_split=2, min_impurity_decrease=0.0, reg_lambda=1.0, reg_alpha=0.0):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_impurity_decrease = min_impurity_decrease
        self.reg_lambda = reg_lambda
        self.reg_alpha = reg_alpha
        self.tree = None

    def fit(self, X, y, sample_weight=None, depth=0):
        if depth < self.max_depth and len(y) >= self.min_samples_split:
            best_split = self._find_best_split(X, y, sample_weight)
            if best_split and best_split['impurity_decrease'] >= self.min_impurity_decrease:
                left_indices, right_indices = self._split(X[:, best_split['feature']], best_split['threshold'])
                self.tree = {
                    'feature': best_split['feature'],
                    'threshold': best_split['threshold'],
                    'left': DecisionTree(self.max_depth, self.min_samples_split, self.min_impurity_decrease, self.reg_lambda, self.reg_alpha).fit(
                        X[left_indices], y[left_indices], sample_weight[left_indices] if sample_weight is not None else None, depth + 1
                    ),
                    'right': DecisionTree(self.max_depth, self.min_samples_split, self.min_impurity_decrease, self.reg_lambda, self.reg_alpha).fit(
                        X[right_indices], y[right_indices], sample_weight[right_indices] if sample_weight is not None else None, depth + 1
                    )
                }
            else:
                self.tree = np.mean(y)
        else:
            self.tree = np.mean(y)
        return self

    def predict(self, X):
        if isinstance(self.tree, dict):
            feature = self.tree['feature']
            threshold = self.tree['threshold']
            left_tree = self.tree['left']
            right_tree = self.tree['right']
            left_indices = X[:, feature] < threshold
            right_indices = ~left_indices
            predictions = np.zeros(X.shape[0])
            predictions[left_indices] = left_tree.predict(X[left_indices])
            predictions[right_indices] = right_tree.predict(X[right_indices])
            return predictions
        else:
            return np.full(X.shape[0], self.tree)

    def _find_best_split(self, X, y, sample_weight):
        best_split = None
        best_loss = float('inf')
        
        for feature in range(X.shape[1]):
            thresholds = np.unique(X[:, feature])
            for threshold in thresholds:
                left_indices, right_indices = self._split(X[:, feature], threshold)
                if len(left_indices) > 0 and len(right_indices) > 0:
                    loss = self._calculate_loss(y[left_indices], y[right_indices], sample_weight[left_indices] if sample_weight is not None else None, sample_weight[right_indices] if sample_weight is not None else None)
                    impurity_decrease = self._impurity_decrease(y, y[left_indices], y[right_indices], sample_weight)
                    if loss < best_loss:
                        best_loss = loss
                        best_split = {'feature': feature, 'threshold': threshold, 'impurity_decrease': impurity_decrease}
        return best_split

    def _split(self, feature_column, threshold):
        left_indices = np.where(feature_column < threshold)[0]
        right_indices = np.where(feature_column >= threshold)[0]
        return left_indices, right_indices

    def _calculate_loss(self, left_targets, right_targets, left_weights=None, right_weights=None):
        if left_weights is None:
            left_loss = np.var(left_targets) * len(left_targets)
        else:
            left_loss = np.average((left_targets - np.mean(left_targets))**2, weights=left_weights)
        if right_weights is None:
            right_loss = np.var(right_targets) * len(right_targets)
        else:
            right_loss = np.average((right_targets - np.mean(right_targets))**2, weights=right_weights)
        loss = left_loss + right_loss + self.reg_lambda * (np.sum(left_targets**2) + np.sum(right_targets**2)) + self.reg_alpha * (np.sum(np.abs(left_targets)) + np.sum(np.abs(right_targets)))
        return loss

    def _impurity_decrease(self, parent, left, right, sample_weight=None):
        if sample_weight is None:
            return np.var(parent) - (len(left) / len(parent) * np.var(left) + len(right) / len(parent) * np.var(right))
        else:
            parent_weight = np.sum(sample_weight)
            left_weight = np.sum(sample_weight[:len(left)])
            right_weight = np.sum(sample_weight[len(left):])
            return np.average((parent - np.mean(parent))**2, weights=sample_weight) - (left_weight / parent_weight * np.average((left - np.mean(left))**2, weights=sample_weight[:len(left)]) + right_weight / parent_weight * np.average((right - np.mean(right))**2, weights=sample_weight[len(left):]))

class XGBoost:
    def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3, min_samples_split=2, min_impurity_decrease=0.0, reg_lambda=1.0, reg_alpha=0.0, early_stopping_rounds=None, learning_rate_decay=1.0, n_jobs=1):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_impurity_decrease = min_impurity_decrease
        self.reg_lambda = reg_lambda
        self.reg_alpha = reg_alpha
        self.early_stopping_rounds = early_stopping_rounds
        self.learning_rate_decay = learning_rate_decay
        self.n_jobs = n_jobs
        self.trees = []

    def fit(self, X, y, X_val=None, y_val=None):
        self.base_prediction = np.mean(y)
        predictions = np.full(y.shape, self.base_prediction)
        best_val_score = float('inf')
        rounds_no_improve = 0

        for i in range(self.n_estimators):
            residuals = self._compute_gradients(y, predictions)
            tree = DecisionTree(self.max_depth, self.min_samples_split, self.min_impurity_decrease, self.reg_lambda, self.reg_alpha).fit(X, residuals)
            update = tree.predict(X)
            predictions += self.learning_rate * update
            self.trees.append(tree)

            # Decay learning rate
            self.learning_rate *= self.learning_rate_decay

            if self.early_stopping_rounds and X_val is not None and y_val is not None:
                val_predictions = self.predict(X_val)
                val_score = self._calculate_loss(y_val, val_predictions)
                if val_score < best_val_score:
                    best_val_score = val_score
                    rounds_no_improve = 0
                else:
                    rounds_no_improve += 1
                if rounds_no_improve >= self.early_stopping_rounds:
                    print(f"Early stopping at round {i+1}")
                    break

    def predict(self, X):
        predictions = np.full(X.shape[0], self.base_prediction)
        for tree in self.trees:
            predictions += self.learning_rate * tree.predict(X)
        return predictions

    def _compute_gradients(self, y, predictions):
        return y - predictions

    def _calculate_loss(self, y_true, y_pred):
        return np.mean((y_true - y_pred) ** 2) + self.reg_lambda * np.sum(np.square(y_pred)) + self.reg_alpha * np.sum(np.abs(y_pred))

# Example usage
if __name__ == "__main__":
    from sklearn.feature_extraction.text import TfidfVectorizer

    # Load data
    column_names = ['text', 'ok', 'sentiment']
    df = pd.read_csv('Tweets.csv', names=column_names, header=None, encoding='latin1')
    df = df.dropna()
    #load only 1000 rows
    
    X, y = df['text'], df['sentiment']

    # Preprocess text data
    vectorizer = TfidfVectorizer(max_features=1000)
    X_transformed = vectorizer.fit_transform(X).toarray()
    
    # Split the data ensuring indices are correctly aligned
    X_train, X_test, y_train, y_test = train_test_split(X_transformed, y.values, test_size=0.2, random_state=42)
    
    # Train XGBoost model
    model = XGBoost(n_estimators=100, learning_rate=0.1, max_depth=3, min_samples_split=2, min_impurity_decrease=0.0, reg_lambda=1.0, reg_alpha=0.0, early_stopping_rounds=10, learning_rate_decay=0.99, n_jobs=-1)
    
    model.fit(X_train, y_train, X_val=X_test, y_val=y_test)
    
    # Predict and evaluate
    y_pred = model.predict(X_test)
    print(f'Mean Squared Error: {mean_squared_error(y_test, y_pred)}')
    print(f'Accuracy: {accuracy_score(y_test, np.round(y_pred))}')
