# ☁️ AI Cloud Smart Storage System

##  Design Project

An intelligent cloud storage system that uses **Machine Learning** to automatically classify files into optimal storage tiers (Hot, Warm, Cold) based on usage patterns.

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python 3 | Backend programming language |
| Flask | Web framework for routing and templates |
| HTML/CSS | Frontend UI (templates) |
| JavaScript | Dashboard charts (Chart.js) |
| AWS S3 | Cloud file storage |
| Scikit-learn | AI/ML model for tier prediction |
| SQLite | Lightweight database for file metadata |

---

## 📁 Project Structure

```
project/
│
├── app.py                  # Main Flask application (routes & logic)
├── requirements.txt        # Python package dependencies
├── README.md               # This file
│
├── templates/              # HTML pages (Jinja2 templates)
│   ├── index.html          # Home page with file upload
│   └── dashboard.html      # Analytics dashboard with charts
│
├── static/                 # CSS and static assets
│   └── style.css           # All styles for the application
│
├── ai/                     # AI/ML module
│   ├── __init__.py         # Package initializer
│   ├── train_model.py      # Script to train the ML model
│   └── predict.py          # Prediction function used by the app
│
├── database/               # SQLite database (auto-created)
│   └── storage.db          # File metadata storage
│
└── cloud/                  # AWS S3 integration
    ├── __init__.py         # Package initializer
    └── aws_upload.py       # S3 upload function
```

---

## 🚀 Step-by-Step Setup Instructions

### Step 1: Install Python

Make sure Python 3.8+ is installed:
```bash
python --version
```
If not installed, download from: https://www.python.org/downloads/

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it:
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Required Packages

```bash
pip install -r requirements.txt
```

### Step 4: Train the AI Model

```bash
python ai/train_model.py
```

You should see output like:
```
Training AI Storage Tier Prediction Model
Model Test Results:
  access=50, size=5KB  → hot
  access=20, size=10KB → warm
  access=3,  size=80KB → cold
Training Accuracy: 100.0%
✅ Model saved to: ai/storage_model.pkl
```

### Step 5: Configure AWS S3 (Optional)

If you have an AWS account, set these environment variables:
```bash
# On Windows:
set AWS_ACCESS_KEY_ID=your-access-key
set AWS_SECRET_ACCESS_KEY=your-secret-key
set AWS_BUCKET_NAME=your-bucket-name
set AWS_REGION=us-east-1

# On Mac/Linux:
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_BUCKET_NAME=your-bucket-name
export AWS_REGION=us-east-1
```

> **Note:** The app works WITHOUT AWS configured too! It will use local placeholder URLs instead.

### Step 6: Run the Flask Server

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
```

### Step 7: Open in Browser

Open your web browser and go to:
- **Home Page:** http://localhost:5000
- **Dashboard:** http://localhost:5000/dashboard

---

## 📊 Features

### 1. File Upload System
- Upload files through a web interface
- Files are stored in AWS S3 (or locally if AWS not configured)
- File metadata is saved in SQLite database

### 2. AI Storage Tier Prediction
- Uses a **Decision Tree Classifier** (scikit-learn)
- Predicts storage tier based on access patterns:
  - 🔥 **Hot:** access_count > 30 (frequently accessed)
  - 🌤️ **Warm:** access_count 10-30 (occasionally accessed)
  - ❄️ **Cold:** access_count < 10 (rarely accessed)

### 3. File Access Tracking
- Tracks how many times each file is accessed
- Updates storage tier prediction with each access
- Records last access timestamp

### 4. Analytics Dashboard
- Total files uploaded
- Total storage size
- Access statistics
- Storage tier distribution (Pie Chart)
- Top accessed files (Bar Chart)
- Estimated monthly storage cost

---

## 🤖 How the AI Model Works

1. **Training Data:** We create labeled examples of files with known storage tiers
2. **Algorithm:** Decision Tree Classifier (like a flowchart of questions)
3. **Features:** `access_count` and `file_size`
4. **Output:** Predicted tier — hot, warm, or cold
5. **Fallback:** If the model file doesn't exist, simple rules are used

---


## 📝 License

This project is created for educational purposes as a 3rd Year Engineering Project.