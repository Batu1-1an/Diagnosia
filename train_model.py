import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
import pickle
import os

# Create models directory if it doesn't exist
if not os.path.exists('models'):
    os.makedirs('models')

# Load the dataset
try:
    dataset = pd.read_csv('datasets/Training.csv')
except FileNotFoundError:
    print("Error: 'datasets/Training.csv' not found. Make sure the dataset is in the correct directory.")
    exit()

# Prepare the data
X = dataset.drop('prognosis', axis=1)
y = dataset['prognosis']

# Encode the target variable
le = LabelEncoder()
le.fit(y)
Y = le.transform(y)

# Initialize and train the SVC model
print("Training the SVC model...")
svc = SVC(kernel='linear')
svc.fit(X, Y)
print("Model training complete.")

# Save the trained model
model_path = 'models/svc.pkl'
print(f"Saving the model to {model_path}...")
with open(model_path, 'wb') as f:
    pickle.dump(svc, f)
print("Model saved successfully.")

# Save the label encoder
le_path = 'models/label_encoder.pkl'
print(f"Saving the label encoder to {le_path}...")
with open(le_path, 'wb') as f:
    pickle.dump(le, f)
print("Label encoder saved successfully.")
