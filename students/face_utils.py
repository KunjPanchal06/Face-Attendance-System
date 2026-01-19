from deepface import DeepFace
import numpy as np

def generate_embedding(img_input):
    """
    Generates a face embedding for the given input.
    Input can be a file path (str) or a numpy array (image).
    """
    try:
        # DeepFace.represent handles both paths and numpy arrays
        results = DeepFace.represent(
            img_path=img_input,
            model_name="Facenet512", # Using Facenet512 for better accuracy
            enforce_detection=False,  # Allow processing even if face detection fails/is unsure
            detector_backend="opencv"
        )
        
        if results:
            return results[0]["embedding"]
            
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None