from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

# Global variables for the model and encoders
model = None
label_encoders = {}

# Currency conversion rate (USD to INR) - you can update this as needed
USD_TO_INR_RATE = float(os.environ.get('USD_TO_INR_RATE', 83.0))

def load_model_and_encoders():
    """Load the trained model and label encoders"""
    global model, label_encoders
    
    if os.path.exists('insurance_model.pkl'):
        with open('insurance_model.pkl', 'rb') as f:
            model = pickle.load(f)
    
    if os.path.exists('label_encoders.pkl'):
        with open('label_encoders.pkl', 'rb') as f:
            label_encoders = pickle.load(f)

def train_model():
    """Train the Random Forest model on the insurance dataset"""
    global model, label_encoders
    
    # Load the dataset
    df = pd.read_csv('insurance.csv')
    
    # Create label encoders for categorical variables
    label_encoders = {}
    categorical_columns = ['sex', 'smoker', 'region']
    
    for col in categorical_columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Prepare features and target
    X = df.drop(['charges'], axis=1)
    y = df['charges']
    
    # Train Random Forest model
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=1, n_jobs=-1)
    model.fit(X, y)
    
    # Save the model and encoders
    with open('insurance_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('label_encoders.pkl', 'wb') as f:
        pickle.dump(label_encoders, f)
    
    print("Model trained and saved successfully!")

@app.route('/')
def home():
    """Home page with a simple form"""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Predict insurance charges based on input parameters"""
    try:
        load_model_and_encoders()  # Ensure model is loaded
        # Get input data
        data = request.get_json()
        
        # Extract features
        age = float(data['age'])
        sex = data['sex']
        bmi = float(data['bmi'])
        children = int(data['children'])
        smoker = data['smoker']
        region = data['region']
        
        # Encode categorical variables
        sex_encoded = label_encoders['sex'].transform([sex])[0]
        smoker_encoded = label_encoders['smoker'].transform([smoker])[0]
        region_encoded = label_encoders['region'].transform([region])[0]
        
        # Create feature array
        features = np.array([[age, sex_encoded, bmi, children, smoker_encoded, region_encoded]])
        
        # Check if model is loaded
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded',
                'message': 'Model needs to be trained first'
            }), 500
        
        # Make prediction
        prediction_usd = model.predict(features)[0]
        prediction_inr = prediction_usd * USD_TO_INR_RATE
        
        return jsonify({
            'success': True,
            'predicted_charges_usd': round(prediction_usd, 2),
            'predicted_charges_inr': round(prediction_inr, 2),
            'message': 'Prediction successful'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error in prediction'
        }), 400

@app.route('/train', methods=['POST'])
def train():
    """Retrain the model"""
    try:
        train_model()
        return jsonify({
            'success': True,
            'message': 'Model trained successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error training model'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': model is not None
    })

if __name__ == '__main__':
    # Load model and encoders on startup
    load_model_and_encoders()
    
    # If model doesn't exist, train it
    if model is None:
        print("Training model...")
        train_model()
        load_model_and_encoders()
    
    # Use PORT environment variable for Render deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port) 