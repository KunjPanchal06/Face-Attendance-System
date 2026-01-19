import numpy as np
from students.models import Student

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_matching_student(test_embedding, threshold=0.55):
    best_match = None
    highest_similarity = threshold

    for student in Student.objects.exclude(face_embeddings=None):
        # Check for dimension mismatch (e.g., old 128-dim vs new 512-dim)
        if len(test_embedding) != len(student.face_embeddings):
            print(f"Skipping {student.roll_no}: Dimension mismatch ({len(test_embedding)} vs {len(student.face_embeddings)})")
            continue

        similarity = cosine_similarity(test_embedding, student.face_embeddings)
        print(f"Comparing with {student.roll_no}, similarity={similarity:.3f}")

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = student

    return best_match, highest_similarity