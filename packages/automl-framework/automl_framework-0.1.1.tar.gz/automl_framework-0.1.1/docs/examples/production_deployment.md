# Production Deployment of AutoML Models

## 🚀 Deploying Machine Learning Models

### 1. Basic Model Saving
```python
from automl import AutoML
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

# Load and prepare data
X, y = load_iris(return_X_y=True)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train AutoML model
automl = AutoML(problem_type='classification')
automl.fit(X_train, y_train)

# Save the best model
automl.save_best_model('iris_model.pkl')
```

### 2. Model Loading and Prediction
```python
# Load saved model
loaded_model = automl.load_model('iris_model.pkl')

# Make predictions
new_data = X_test[:5]  # Example new data
predictions = loaded_model.predict(new_data)
```

### 3. Flask REST API Deployment
```python
from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)
model = automl.load_model('iris_model.pkl')

@app.route('/predict', methods=['POST'])
def predict():
    """Simple prediction endpoint"""
    try:
        # Get input data
        data = request.json['features']

        # Convert to numpy array
        input_data = np.array(data).reshape(1, -1)

        # Make prediction
        prediction = model.predict(input_data)

        return jsonify({
            'prediction': prediction.tolist(),
            'success': True
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'success': False
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### 4. Docker Containerization
```dockerfile
# Dockerfile for model deployment
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy model and application code
COPY iris_model.pkl .
COPY app.py .

# Expose prediction service port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]
```

### 5. Model Monitoring
```python
def monitor_model_performance(model, X_test, y_test):
    """
    Basic model performance monitoring
    """
    # Make predictions
    predictions = model.predict(X_test)

    # Calculate performance metrics
    performance = {
        'accuracy': accuracy_score(y_test, predictions),
        'f1_score': f1_score(y_test, predictions, average='weighted'),
        'timestamp': datetime.now()
    }

    # Log performance
    log_model_performance(performance)

    return performance
```

## 🔧 Deployment Considerations

### Performance Optimization
- Use model compression
- Implement caching
- Optimize preprocessing
- Consider model quantization

### Security
- Validate input data
- Implement authentication
- Use HTTPS
- Sanitize predictions

### Scalability
- Use load balancing
- Implement horizontal scaling
- Consider serverless deployment

## 💡 Best Practices
1. Save preprocessor with model
2. Handle input data validation
3. Implement error handling
4. Log model predictions
5. Monitor model performance
6. Version your models

## 🚨 Common Pitfalls
- Forgetting to save preprocessor
- Not handling new data types
- Lack of input validation
- Insufficient error handling
- No performance monitoring

## 🎓 Key Learning Objectives
- ✅ Save and load models
- ✅ Create prediction API
- ✅ Containerize model
- ✅ Implement basic monitoring

---

<div align="center">
🌐 **From Notebook to Production** 🚀

*Transforming models into intelligent services*
</div>
