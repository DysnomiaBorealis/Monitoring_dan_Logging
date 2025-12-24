"""
Model Serving API for Spam Detection
"""

from flask import Flask, request, jsonify
import joblib
import os
from datetime import datetime

app = Flask(__name__)

# Load model and vectorizer on startup
print("Loading model and vectorizer...")
try:
    MODEL_PATH = os.getenv('MODEL_PATH', '/app/models/spam_detection_model.joblib')
    VECTORIZER_PATH = os.getenv('VECTORIZER_PATH', '/app/vectorizer.joblib')
    
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print(f"✓ Model loaded from: {MODEL_PATH}")
    print(f"✓ Vectorizer loaded from: {VECTORIZER_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    vectorizer = None


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model is not None else 'unhealthy',
        'model_loaded': model is not None,
        'vectorizer_loaded': vectorizer is not None,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/invocations', methods=['POST'])
def invocations():
    """
    MLflow-compatible prediction endpoint
    
    Input JSON:
    {
        "inputs": ["text message 1", "text message 2", ...]
    }
    
    OR
    
    {
        "text": "single text message"
    }
    
    Output JSON:
    {
        "predictions": [
            {"prediction": "spam", "confidence": 0.95},
            ...
        ]
    }
    """
    try:
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Check if model is loaded
        if model is None or vectorizer is None:
            return jsonify({'error': 'Model not loaded'}), 500
        
        # Support both formats
        if 'inputs' in request.json:
            texts = request.json['inputs']
            if not isinstance(texts, list):
                texts = [texts]
        elif 'text' in request.json:
            texts = [request.json['text']]
        else:
            return jsonify({'error': 'Missing "inputs" or "text" field'}), 400
        
        # Validate inputs
        if not all(isinstance(t, str) for t in texts):
            return jsonify({'error': 'All inputs must be strings'}), 400
        
        # Vectorize
        X = vectorizer.transform(texts)
        
        # Predict
        predictions = model.predict(X)
        probabilities = model.predict_proba(X)
        
        # Format results
        results = []
        for i, (pred, probs) in enumerate(zip(predictions, probabilities)):
            result = 'spam' if pred == 1 else 'ham'
            confidence = float(probs[pred])
            results.append({
                'prediction': result,
                'confidence': confidence,
                'probabilities': {
                    'ham': float(probs[0]),
                    'spam': float(probs[1])
                }
            })
        
        return jsonify({
            'predictions': results,
            'model_version': '1.0',
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/', methods=['GET'])
def home():
    """Home endpoint with API information"""
    return jsonify({
        'service': 'Spam Detection Model Serving API',
        'author': 'Yudhistira Paksi (dysnomia)',
        'version': '1.0',
        'endpoints': {
            '/invocations': 'POST - Make predictions (MLflow compatible)',
            '/health': 'GET - Health check'
        },
        'example_request': {
            'url': '/invocations',
            'method': 'POST',
            'body': {
                'inputs': ['CONGRATULATIONS! You won!']
            }
        }
    })


if __name__ == '__main__':
    print("=" * 60)
    print("SPAM DETECTION MODEL SERVING API")
    print("=" * 60)
    print(f"Author: Yudhistira Paksi (dysnomia)")
    print(f"Starting server on http://0.0.0.0:5001")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
