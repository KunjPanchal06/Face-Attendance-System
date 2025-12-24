from django.http import JsonResponse
from students.face_utils import generate_embedding
from attendance.face_matcher import find_matching_student
from attendance.services import mark_attendance
from django.shortcuts import render

def mark_attendance_view(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        embedding = generate_embedding(image)

        student, similarity = find_matching_student(embedding)

        if student:
            attendance, created = mark_attendance(student)
            return JsonResponse({
                "status": "success",
                "student": student.roll_no,
                "similarity": similarity,
                "marked": created
            })

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