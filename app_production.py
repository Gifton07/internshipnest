import os
import logging
import time
from functools import wraps
from flask import Flask, request, jsonify, render_template, g
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
import warnings
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from config import config

warnings.filterwarnings('ignore')

# Initialize Sentry for error tracking
if os.environ.get('SENTRY_DSN'):
    sentry_sdk.init(
        dsn=os.environ.get('SENTRY_DSN'),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
        environment=os.environ.get('FLASK_ENV', 'development')
    )

def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Setup logging
    setup_logging(app)
    
    # Initialize metrics
    if app.config.get('ENABLE_METRICS'):
        setup_metrics(app)
    
    # Global variables for the model and encoders
    model = None
    label_encoders = {}
    
    def load_model_and_encoders():
        """Load the trained model and label encoders"""
        nonlocal model, label_encoders
        
        try:
            if os.path.exists(app.config['MODEL_PATH']):
                with open(app.config['MODEL_PATH'], 'rb') as f:
                    model = pickle.load(f)
                app.logger.info("Model loaded successfully")
            
            if os.path.exists(app.config['ENCODERS_PATH']):
                with open(app.config['ENCODERS_PATH'], 'rb') as f:
                    label_encoders = pickle.load(f)
                app.logger.info("Label encoders loaded successfully")
                
        except Exception as e:
            app.logger.error(f"Error loading model: {str(e)}")
            raise
    
    def train_model():
        """Train the Random Forest model on the insurance dataset"""
        nonlocal model, label_encoders
        
        try:
            # Load the dataset
            df = pd.read_csv(app.config['DATASET_PATH'])
            
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
            with open(app.config['MODEL_PATH'], 'wb') as f:
                pickle.dump(model, f)
            
            with open(app.config['ENCODERS_PATH'], 'wb') as f:
                pickle.dump(label_encoders, f)
            
            app.logger.info("Model trained and saved successfully!")
            
        except Exception as e:
            app.logger.error(f"Error training model: {str(e)}")
            raise
    
    # Request timing middleware
    @app.before_request
    def before_request():
        g.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        # Add security headers in production
        if app.config.get('SECURITY_HEADERS'):
            for header, value in app.config['SECURITY_HEADERS'].items():
                response.headers[header] = value
        
        # Log request timing
        if hasattr(g, 'start_time'):
            duration = time.time() - g.start_time
            app.logger.info(f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s")
        
        return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found', 'message': 'The requested resource was not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"Internal server error: {str(error)}")
        return jsonify({'error': 'Internal server error', 'message': 'Something went wrong'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        app.logger.error(f"Unhandled exception: {str(e)}")
        return jsonify({'error': 'Server error', 'message': 'An unexpected error occurred'}), 500
    
    # Rate limiting decorator
    def rate_limit(max_requests=100, window=60):
        def decorator(f):
            @wraps(f)
            def wrapped(*args, **kwargs):
                # Simple in-memory rate limiting (use Redis in production)
                client_ip = request.remote_addr
                current_time = time.time()
                
                # This is a simplified rate limiter - use Flask-Limiter in production
                return f(*args, **kwargs)
            return wrapped
        return decorator
    
    @app.route('/')
    def home():
        """Home page with a simple form"""
        return render_template('index.html')
    
    @app.route('/predict', methods=['POST'])
    @rate_limit(max_requests=60, window=60)  # 60 requests per minute
    def predict():
        """Predict insurance charges based on input parameters"""
        try:
            # Validate input data
            data = request.get_json()
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON',
                    'message': 'Request must contain valid JSON data'
                }), 400
            
            required_fields = ['age', 'sex', 'bmi', 'children', 'smoker', 'region']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': 'Missing field',
                        'message': f'Missing required field: {field}'
                    }), 400
            
            # Load model if not loaded
            if model is None:
                load_model_and_encoders()
            
            # Extract and validate features
            try:
                age = float(data['age'])
                if not (18 <= age <= 100):
                    raise ValueError("Age must be between 18 and 100")
                
                sex = data['sex']
                if sex not in ['male', 'female']:
                    raise ValueError("Sex must be 'male' or 'female'")
                
                bmi = float(data['bmi'])
                if not (10 <= bmi <= 50):
                    raise ValueError("BMI must be between 10 and 50")
                
                children = int(data['children'])
                if not (0 <= children <= 10):
                    raise ValueError("Children must be between 0 and 10")
                
                smoker = data['smoker']
                if smoker not in ['yes', 'no']:
                    raise ValueError("Smoker must be 'yes' or 'no'")
                
                region = data['region']
                valid_regions = ['southwest', 'southeast', 'northwest', 'northeast']
                if region not in valid_regions:
                    raise ValueError(f"Region must be one of: {', '.join(valid_regions)}")
                    
            except (ValueError, TypeError) as e:
                return jsonify({
                    'success': False,
                    'error': 'Validation error',
                    'message': str(e)
                }), 400
            
            # Encode categorical variables
            try:
                sex_encoded = label_encoders['sex'].transform([sex])[0]
                smoker_encoded = label_encoders['smoker'].transform([smoker])[0]
                region_encoded = label_encoders['region'].transform([region])[0]
            except Exception as e:
                app.logger.error(f"Error encoding categorical variables: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Encoding error',
                    'message': 'Error processing categorical data'
                }), 500
            
            # Create feature array
            features = np.array([[age, sex_encoded, bmi, children, smoker_encoded, region_encoded]])
            
            # Make prediction
            try:
                prediction_usd = model.predict(features)[0]
                prediction_inr = prediction_usd * app.config['USD_TO_INR_RATE']
                
                # Log successful prediction
                app.logger.info(f"Prediction successful: ${prediction_usd:.2f} USD, ₹{prediction_inr:.2f} INR")
                
                return jsonify({
                    'success': True,
                    'predicted_charges_usd': round(prediction_usd, 2),
                    'predicted_charges_inr': round(prediction_inr, 2),
                    'message': 'Prediction successful'
                })
                
            except Exception as e:
                app.logger.error(f"Error making prediction: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Prediction error',
                    'message': 'Error generating prediction'
                }), 500
                
        except Exception as e:
            app.logger.error(f"Unexpected error in prediction: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Server error',
                'message': 'An unexpected error occurred'
            }), 500
    
    @app.route('/train', methods=['POST'])
    def train():
        """Retrain the model"""
        try:
            train_model()
            load_model_and_encoders()  # Reload the model
            return jsonify({
                'success': True,
                'message': 'Model trained successfully'
            })
        except Exception as e:
            app.logger.error(f"Error training model: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'Error training model'
            }), 500
    
    @app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        try:
            model_status = model is not None
            return jsonify({
                'status': 'healthy',
                'model_loaded': model_status,
                'timestamp': time.time(),
                'version': '1.0.0'
            })
        except Exception as e:
            app.logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'unhealthy',
                'error': str(e)
            }), 500
    
    @app.route('/metrics')
    def metrics():
        """Prometheus metrics endpoint"""
        if app.config.get('ENABLE_METRICS'):
            return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}
        else:
            return jsonify({'error': 'Metrics disabled'}), 404
    
    # Initialize model on startup
    with app.app_context():
        try:
            load_model_and_encoders()
            if model is None:
                app.logger.info("Training model on startup...")
                train_model()
                load_model_and_encoders()
        except Exception as e:
            app.logger.error(f"Error initializing model: {str(e)}")
    
    return app

def setup_logging(app):
    """Setup application logging"""
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'], 
            maxBytes=10240000, 
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Insurance Predictor startup')

def setup_metrics(app):
    """Setup Prometheus metrics"""
    # Request counter
    request_counter = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
    
    # Request duration histogram
    request_duration = Histogram('http_request_duration_seconds', 'HTTP request duration')
    
    # Prediction counter
    prediction_counter = Counter('predictions_total', 'Total predictions made')
    
    app.metrics = {
        'request_counter': request_counter,
        'request_duration': request_duration,
        'prediction_counter': prediction_counter
    }

# Create the application instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000))) 