import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class NaiveBayesClassifier:
    def __init__(self):
        self.priors = {}
        self.likelihoods = {}
        self.classes = None
        self.vocab_size = 0

    def fit(self, X, y):
        self.classes = np.unique(y)
        self.vocab_size = X.shape[1]
        self.priors = {cls: np.mean(y == cls) for cls in self.classes}
        self.likelihoods = {cls: np.zeros(self.vocab_size) for cls in self.classes}

        for cls in self.classes:
            X_cls = X[y == cls]
            self.likelihoods[cls] = (np.sum(X_cls, axis=0) + 1) / (np.sum(X_cls) + self.vocab_size)  # Laplace smoothing

    def predict(self, X):
        predictions = []
        for x in X:
            posteriors = {}
            for cls in self.classes:
                prior = np.log(self.priors[cls])
                likelihood = np.sum(np.log(self.likelihoods[cls]) * x)
                posteriors[cls] = prior + likelihood
            predictions.append(max(posteriors, key=posteriors.get))
        return predictions

# Example usage
if __name__ == "__main__":
    # Sample sentiment analysis data
    column_names = ['text', 'ok', 'sentiment']
    df = pd.read_csv('Tweets.csv', names=column_names, header=None, encoding='latin1')
    df = df.dropna()

    # Vectorize the text data
    vectorizer = TfidfVectorizer()
    X_vectorized = vectorizer.fit_transform(df['text'])

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_vectorized.toarray(), df['sentiment'], test_size=0.2, random_state=42)

    # Train the Naive Bayes classifier
    nb = NaiveBayesClassifier()
    nb.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = nb.predict(X_test)

    # Evaluate the model
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)

    print("Accuracy:", accuracy)
    print("Classification Report:\n", report)
