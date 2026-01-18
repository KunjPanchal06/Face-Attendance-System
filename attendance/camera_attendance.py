import cv2
import tempfile
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
            # Save frame temporarily
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                temp_image_path = tmp.name
                cv2.imwrite(temp_image_path, frame)

            try:
                embedding = generate_embedding(temp_image_path)
                student, similarity = find_matching_student(embedding)

                if student:
                    attendance, created = mark_attendance(student)
                    print(
                        f"Attendance marked for {student.roll_no} "
                        f"(similarity={similarity:.2f})"
                    )
                else:
                    print("No matching student found")

            except Exception as e:
                print("Error:", e)

            finally:
                os.remove(temp_image_path)

        # Quit
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
