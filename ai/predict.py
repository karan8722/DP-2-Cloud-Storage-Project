"""
=============================================================================
AI Prediction Module
=============================================================================
This module loads the trained AI model and makes predictions.

It predicts which storage tier a file should be placed in:
  - HOT:  Fast access, expensive     (frequently used files)
  - WARM: Medium access, moderate    (occasionally used files)
  - COLD: Slow access, cheap         (rarely used files)

Usage:
    from ai.predict import predict_storage_tier
    tier = predict_storage_tier(access_count=50, file_size=10000)
    # Returns: 'hot'
=============================================================================
"""

import sys

# verify required libraries are installed
try:
    import joblib
    import numpy as np
except ImportError as imp_err:
    print("Error: required AI libraries are missing (joblib/numpy).\n" \
          "Please install dependencies with:\n" \
          "    pip install -r requirements.txt\n" \
          "or activate the project virtual environment.")
    sys.exit(1)

import os


# Mapping from model output (numbers) to tier names (strings)
TIER_NAMES = {
    0: 'cold',    # Rarely accessed → cheap storage
    1: 'warm',    # Sometimes accessed → medium storage
    2: 'hot'      # Frequently accessed → fast storage
}


def predict_storage_tier(access_count, file_size):
    """
    Predict the storage tier for a file using the trained AI model.
    
    Parameters:
        access_count (int): How many times the file has been accessed
        file_size (int): Size of the file in bytes
    
    Returns:
        str: 'hot', 'warm', or 'cold'
    
    How it works:
        1. Try to load the trained model from disk
        2. If model exists → use AI prediction
        3. If model doesn't exist → use simple rule-based fallback
    """
    model_path = 'ai/storage_model.pkl'
    
    # Check if the trained model file exists
    if os.path.exists(model_path):
        # ── Use AI Model ──────────────────────────────────────────────────
        try:
            # Load the trained model
            model = joblib.load(model_path)
            
            # Prepare input data (must be 2D array for scikit-learn)
            input_data = np.array([[access_count, file_size]])
            
            # Make prediction
            prediction = model.predict(input_data)[0]
            
            # Convert number to tier name
            tier = TIER_NAMES.get(prediction, 'cold')
            
            print(f"🤖 AI Prediction: access={access_count}, size={file_size} → {tier}")
            return tier
            
        except Exception as e:
            print(f"⚠️ Model prediction failed: {e}")
            # Fall through to rule-based prediction
    
    # ── Fallback: Simple Rule-Based Prediction ────────────────────────────
    # Used when the AI model hasn't been trained yet
    print("📋 Using rule-based prediction (model not trained yet)")
    
    if access_count > 30:
        return 'hot'       # High access → hot storage
    elif access_count >= 10:
        return 'warm'      # Medium access → warm storage
    else:
        return 'cold'      # Low access → cold storage
