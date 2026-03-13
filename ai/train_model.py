"""
=============================================================================
AI Model Training Script
=============================================================================
This script trains a simple machine learning model using scikit-learn.

What does this model do?
  - It predicts the STORAGE TIER (hot, warm, cold) for a file
  - Based on: access_count and file_size

Storage Tiers Explained:
  - HOT:  Frequently accessed files → stored on fast (expensive) storage
  - WARM: Occasionally accessed files → stored on medium-speed storage  
  - COLD: Rarely accessed files → stored on slow (cheap) storage

Algorithm Used: Decision Tree Classifier
  - Simple, easy to understand
  - Works like a flowchart of yes/no questions
  - Perfect for this classification task

How to run:
  python ai/train_model.py
=============================================================================
"""

import sys

# ensure required ML library is available; give user a helpful message if not
try:
    from sklearn.tree import DecisionTreeClassifier
except ImportError:
    print("Error: scikit-learn is not installed.\n" \
          "Please install the project dependencies (see requirements.txt) with:\n" \
          "    pip install -r requirements.txt\n" \
          "or activate your virtual environment if one is used.")
    sys.exit(1)

import joblib
import numpy as np
import os

def train_model():
    """
    Train the AI model and save it to a file.
    
    Steps:
    1. Create training data (features and labels)
    2. Train the Decision Tree model
    3. Save the model to disk using joblib
    """
    
    # ─── Step 1: Create Training Data ─────────────────────────────────────
    # Each row = [access_count, file_size_in_bytes]
    # We create sample data that represents different usage patterns
    
    X_train = np.array([
        # Hot storage examples (high access count)
        [100, 5000],    [80, 10000],   [50, 2000],    [45, 8000],
        [60, 15000],    [70, 3000],    [55, 12000],   [90, 7000],
        [35, 4000],     [40, 6000],    [31, 9000],    [65, 1000],
        [42, 20000],    [38, 11000],   [75, 5500],    [85, 2500],
        
        # Warm storage examples (medium access count)
        [25, 5000],     [20, 10000],   [15, 20000],   [28, 3000],
        [18, 8000],     [22, 15000],   [12, 4000],    [29, 7000],
        [16, 12000],    [24, 6000],    [11, 9000],    [27, 1000],
        [14, 25000],    [19, 11000],   [23, 5500],    [26, 2500],
        
        # Cold storage examples (low access count)
        [5, 50000],     [2, 100000],   [0, 20000],    [8, 30000],
        [1, 80000],     [3, 45000],    [7, 60000],    [9, 10000],
        [4, 70000],     [6, 40000],    [0, 150000],   [1, 90000],
        [3, 55000],     [2, 35000],    [5, 25000],    [8, 15000],
    ])
    
    # Labels: what storage tier each example should be classified as
    # 0 = cold, 1 = warm, 2 = hot
    y_train = np.array([
        # Hot (access_count > 30)
        2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
        # Warm (access_count 10-30)
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        # Cold (access_count < 10)
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ])
    
    # ─── Step 2: Train the Model ──────────────────────────────────────────
    # DecisionTreeClassifier creates a tree of if/else rules
    # max_depth=5 prevents the tree from being too complex (overfitting)
    
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)  # Train the model on our data
    
    # ─── Step 3: Test the Model ───────────────────────────────────────────
    # Quick test to make sure it works
    test_data = np.array([[50, 5000], [20, 10000], [3, 80000]])
    predictions = model.predict(test_data)
    
    tier_names = {0: 'cold', 1: 'warm', 2: 'hot'}
    print("Model Test Results:")
    print(f"  access=50, size=5KB  → {tier_names[predictions[0]]}")   # Should be: hot
    print(f"  access=20, size=10KB → {tier_names[predictions[1]]}")   # Should be: warm
    print(f"  access=3,  size=80KB → {tier_names[predictions[2]]}")   # Should be: cold
    
    # Calculate accuracy on training data
    accuracy = model.score(X_train, y_train)
    print(f"\nTraining Accuracy: {accuracy * 100:.1f}%")
    
    # ─── Step 4: Save the Model ───────────────────────────────────────────
    # joblib saves the trained model to a file
    # We can load it later in predict.py without re-training
    
    os.makedirs('ai', exist_ok=True)
    model_path = 'ai/storage_model.pkl'
    joblib.dump(model, model_path)
    print(f"\n✅ Model saved to: {model_path}")
    print("You can now use predict.py to make predictions!")


# Run the training when this script is executed directly
if __name__ == '__main__':
    print("=" * 60)
    print("Training AI Storage Tier Prediction Model")
    print("=" * 60)
    train_model()
