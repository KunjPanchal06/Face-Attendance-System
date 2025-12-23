import face_recognition_module
import numpy as np
from PIL import Image   

def generate_embedding(image_file):
    img = face_recognition_module.load_image_file(image_file)

    encodings = face_recognition_module.face_encodings(img)

    if len(encodings) == 0:
        return None

    return encodings[0].tolist()
