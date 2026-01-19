from django.http import JsonResponse
from students.face_utils import generate_embedding
from attendance.face_matcher import find_matching_student
from attendance.services import mark_attendance
from django.shortcuts import render, redirect
from django.contrib import messages
# from attendance.camera_attendance import start_camera_attendance

def mark_attendance_view(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        embedding = generate_embedding(image)

        student, similarity = find_matching_student(embedding)

        if student:
            print(f"MATCH FOUND: Student {student.roll_no} with similarity {similarity}")
            attendance, created = mark_attendance(student)
            print(f"Attendance marked: {created}")
            return JsonResponse({
                "status": "success",
                "student": f"{student.full_name} ({student.roll_no})",
                "similarity": similarity,
                "marked": created
            })

        print(f"NO MATCH FOUND. Max similarity was likely below threshold.")
        return JsonResponse({"status": "no_match"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)

def test_attendance_page(request):
    result = None

    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        embedding = generate_embedding(image)
        student, similarity = find_matching_student(embedding)

        if student:
            attendance, created = mark_attendance(student)
            result = f"Matched {student.roll_no}, similarity={similarity:.2f}"
        else:
            result = "No match found"

    return render(request, "attendance_test.html", {"result": result})

def start_attendance_session(request):
    """
    Renders the frontend page for live attendance.
    The actual processing happens via AJAX calls to mark_attendance_view.
    """
    return render(request, "attendance/attendance_session.html")