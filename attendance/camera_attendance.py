import cv2
import os
import django

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "face_attendance.settings"
)

django.setup()



from students.face_utils import generate_embedding
from attendance.face_matcher import find_matching_student
from attendance.services import mark_attendance


def start_camera_attendance():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Cannot access camera")
        return

    print("Camera started. Press 'c' to capture, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        cv2.imshow("Face Attendance - Press C to Capture", frame)

        key = cv2.waitKey(1) & 0xFF

        # Capture frame
        if key == ord("c"):
            # We can pass the frame directly to generate_embedding now!
            try:
                # Use robust single embedding for recognition
                embedding = generate_embedding(frame)
                
                if embedding:
                    student, similarity = find_matching_student(embedding)

                    if student:
                        attendance, created = mark_attendance(student)
                        status_msg = "Marked Present" if created else "Already Marked"
                        print(
                            f"Success: {student.roll_no} - {status_msg} "
                            f"(similarity={similarity:.2f})"
                        )
                    else:
                        print("No matching student found")
                else:
                    print("No face detected in the frame")

            except Exception as e:
                print("Error:", e)

        # Quit
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
