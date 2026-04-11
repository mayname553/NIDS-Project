import joblib
import os
import tensorflow as tf

def test_load():
    model_path = 'model/hybrid_nids_model.keras'
    preprocessor_path = 'model/preprocessor.pkl'
    
    print(f"Testing model_path: {model_path}, exists: {os.path.exists(model_path)}")
    print(f"Testing preprocessor_path: {preprocessor_path}, exists: {os.path.exists(preprocessor_path)}")
    
    try:
        print("Loading Keras model using absolute path...")
        abs_model_path = os.path.abspath(model_path)
        print(f"Absolute path: {abs_model_path}")
        # Try to use a relative path with ./
        model = tf.keras.models.load_model(f"./{model_path}")
        print("Keras model loaded.")
        
        print("Loading Joblib preprocessor...")
        data = joblib.load(preprocessor_path)
        print("Joblib preprocessor loaded.")
        print(f"Keys: {data.keys()}")
    except Exception as e:
        print(f"Error during load: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_load()
