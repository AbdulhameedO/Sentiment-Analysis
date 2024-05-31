import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.linear_model import LogisticRegression


# Load the dataset
# Specify the column names
column_names = ['text','ok', 'sentiment']

# Load the dataset
# Load the dataset
df = pd.read_csv('Tweets.csv', names=column_names, header=None, encoding='latin1')
df=df.dropna()
# Split the dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(df['text'], df['sentiment'], test_size=0.2, random_state=0)
# Convert the text into counts
vectorizer = CountVectorizer()
X_train_counts = vectorizer.fit_transform(X_train)
X_test_counts = vectorizer.transform(X_test)

# Train the model
# Train the model
clf = LogisticRegression(random_state=0, max_iter=1000)
clf.fit(X_train_counts, y_train)

# Test the model
y_pred = clf.predict(X_test_counts)
print('Accuracy:', accuracy_score(y_test, y_pred))
#save the model

