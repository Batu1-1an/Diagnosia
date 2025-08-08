import pandas as pd
import pickle
import os
import ast
import numpy as np
from constants import SYMPTOMS_DICT, DISEASES_LIST

def load_prediction_model():
    """Loads the pre-trained SVC model."""
    try:
        model_path = os.path.join(os.path.dirname(__file__), 'models', 'svc.pkl')
        with open(model_path, 'rb') as f:
            svc = pickle.load(f)
        return svc
    except FileNotFoundError:
        print("Error: 'models/svc.pkl' not found. Please run train_model.py first.")
        return None

def load_recommendation_data():
    """Loads all the recommendation CSV files into pandas DataFrames."""
    data_path = os.path.join(os.path.dirname(__file__), 'datasets')
    try:
        sym_des = pd.read_csv(os.path.join(data_path, "Symptom-severity.csv"))
        precautions = pd.read_csv(os.path.join(data_path, "precautions_df.csv"))
        workout = pd.read_csv(os.path.join(data_path, "workout_df.csv"))
        description = pd.read_csv(os.path.join(data_path, "description.csv"))
        medications = pd.read_csv(os.path.join(data_path, 'medications.csv'))
        diets = pd.read_csv(os.path.join(data_path, "diets.csv"))
        return sym_des, precautions, workout, description, medications, diets
    except FileNotFoundError as e:
        print(f"Error loading recommendation data: {e}")
        return None, None, None, None, None, None

# Load data at module import time
svc_model = load_prediction_model()
(sym_des_df, precautions_df, workout_df, description_df, medications_df, diets_df) = load_recommendation_data()

def get_predicted_value(patient_symptoms):
    """Predicts the disease based on patient symptoms."""
    if svc_model is None:
        return "Error: Model not loaded"
    input_vector = np.zeros(len(SYMPTOMS_DICT))
    for item in patient_symptoms:
        if item in SYMPTOMS_DICT:
            input_vector[SYMPTOMS_DICT[item]] = 1
    return DISEASES_LIST[svc_model.predict([input_vector])[0]]

def get_recommendations(disease):
    """Gets recommendations for a given disease."""
    if description_df is None:
        return "Error: Recommendation data not loaded", [], [], [], []

    desc = description_df[description_df['Disease'] == disease]['Description']
    desc = " ".join([w for w in desc])

    pre = precautions_df[precautions_df['Disease'] == disease][['Precaution_1', 'Precaution_2', 'Precaution_3', 'Precaution_4']]
    pre = [col for col in pre.values]

    med = medications_df[medications_df['Disease'] == disease]['Medication']
    med = [ast.literal_eval(m) if isinstance(m, str) else m for m in med.values]
    med = med[0] if med else []

    die = diets_df[diets_df['Disease'] == disease]['Diet']
    die = [ast.literal_eval(d) if isinstance(d, str) else d for d in die.values]
    die = die[0] if die else []

    wrkout = workout_df[workout_df['disease'] == disease]['workout']
    wrkout = wrkout.tolist()

    return desc, pre, med, die, wrkout
