import numpy as np
from students.models import Student

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def find_matching_student(test_embedding, threshold=0.7):
    best_match = None
    highest_similarity = threshold

    for student in Student.objects.exclude(face_embedding=None):
        similarity = cosine_similarity(test_embedding, student.face_embedding)

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = student

    return best_match, highest_similarity