from pathlib import Path
import joblib
import pickle

# Try optional ML libraries
try:
    import torch
except ImportError:
    torch = None

try:
    import xgboost
except ImportError:
    xgboost = None

try:
    import sklearn
except ImportError:
    sklearn = None

try:
    import tensorflow as tf
    from tensorflow import keras
except ImportError:
    tf = keras = None


def find_latest_model():
    """Find the most recently modified model file in the current directory."""
    exts = ['.pkl', '.joblib', '.pt', '.h5']
    files = [f for f in Path('.').iterdir() if f.is_file() and f.suffix in exts]
    print(f"[DEBUG] Found model files: {[f.name for f in files]}")
    if not files:
        raise FileNotFoundError("No supported model files found (.pkl, .joblib, .pt, .h5)")
    latest = max(files, key=lambda f: f.stat().st_mtime)
    print(f"[DEBUG] Latest model file selected: {latest}")
    return latest


def load_model(file_path):
    """Load the model based on its file extension."""
    path = Path(file_path)
    print(f"[DEBUG] Attempting to load: {path.name} (extension: {path.suffix})")
    
    if path.suffix in ['.pkl', '.joblib']:
        try:
            model = joblib.load(path)
            print("[DEBUG] Successfully loaded model using joblib.")
            return model
        except Exception as e:
            print(f"[DEBUG] joblib failed: {e}. Trying with pickle...")
            with open(path, 'rb') as f:
                model = pickle.load(f)
                print("[DEBUG] Successfully loaded model using pickle.")
                return model

    elif path.suffix == '.pt':
        if torch:
            try:
                model = torch.load(path)
                print("[DEBUG] Successfully loaded model using PyTorch.")
                return model
            except Exception as e:
                print(f"[ERROR] PyTorch loading failed: {e}")
                raise
        else:
            raise ImportError("PyTorch is not installed but required to load this model.")

    elif path.suffix == '.h5':
        if keras:
            try:
                model = keras.models.load_model(path)
                print("[DEBUG] Successfully loaded model using Keras.")
                return model
            except Exception as e:
                print(f"[ERROR] Keras loading failed: {e}")
                raise
        else:
            raise ImportError("Keras/TensorFlow is not installed but required to load this model.")

    else:
        raise ValueError(f"Unsupported model format or missing library for extension: {path.suffix}")


def extract_framework(model):
    """Guess the framework of the given model object."""
    cls = str(type(model)).lower()
    print(f"[DEBUG] Detected model class type: {cls}")

    if "sklearn" in cls:
        return "sklearn"
    elif "xgboost" in cls:
        return "xgboost"
    elif "keras" in cls or "tensorflow" in cls:
        return "keras"
    elif "torch" in cls:
        return "pytorch"
    else:
        return "unknown"