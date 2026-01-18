from deepface import DeepFace

def generate_embedding(image_path):
    embeddings = DeepFace.represent(
        img_path=image_path,
        model_name="Facenet",
        enforce_detection=False
    )

    # DeepFace returns a list of results
    return embeddings[0]["embedding"]