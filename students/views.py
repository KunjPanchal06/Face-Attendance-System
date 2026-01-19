import json
import base64
import numpy as np
import cv2
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from classrooms.models import Classroom
from .models import Student
from .face_utils import generate_embedding
from django.contrib.auth.models import User
from users.models import UserRole

def student_list_view(request):
    """Renders the list of all students."""
    students = Student.objects.select_related('classroom').all()
    classrooms = Classroom.objects.all()
    return render(request, 'students/student_list.html', {'students': students, 'classrooms': classrooms})

def student_create_view(request):
    """Renders the student registration page with classroom options."""
    classrooms = Classroom.objects.all()
    return render(request, 'students/student_create.html', {'classrooms': classrooms})

@csrf_exempt
def register_student_api(request):
    """
    API endpoint to register a new student.
    Expects JSON payload:
    {
        "full_name": "Name",
        "roll_no": "123",
        "classroom_id": 1,
        "images": ["base64_str_1", "base64_str_2", ...]
    }
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        from django.contrib.auth.models import User
        from users.models import UserRole
        
        data = json.loads(request.body)
        
        full_name = data.get("full_name")
        roll_no = data.get("roll_no")
        classroom_id = data.get("classroom_id")
        images_base64 = data.get("images", [])

        # Basic Validation
        if not all([full_name, roll_no, classroom_id]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        if Student.objects.filter(roll_no=roll_no).exists():
            return JsonResponse({"error": "Student with this Roll Number already exists"}, status=400)

        if not images_base64 or len(images_base64) < 5:
             return JsonResponse({"error": "Insufficient face data captured"}, status=400)

        # Process Images & Generate Embeddings
        valid_embeddings = []
        
        for img_str in images_base64:
            try:
                # Decode base64
                if "," in img_str:
                    img_str = img_str.split(",")[1]
                
                img_data = base64.b64decode(img_str)
                np_arr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                # Generate embedding
                embedding = generate_embedding(img)
                if embedding:
                    valid_embeddings.append(embedding)
            except Exception as e:
                print(f"Error processing image frame: {e}")
                continue

        if not valid_embeddings:
            return JsonResponse({"error": "Could not extract face features from any image"}, status=400)

        # Calculate logical average embedding (centroid)
        avg_embedding = np.mean(valid_embeddings, axis=0).tolist()

        # Create Student
        with transaction.atomic():
            # Create User
            # Use roll_no as username and initial password
            user = User.objects.create_user(username=roll_no, password=roll_no)
            
            # Assign 'student' role
            UserRole.objects.create(user=user, role='student')

            classroom = Classroom.objects.get(id=classroom_id)
            student = Student.objects.create(
                user=user,
                full_name=full_name,
                roll_no=roll_no,
                classroom=classroom,
                face_embeddings=avg_embedding # Storing the list/vector directly
            )

        return JsonResponse({
            "status": "success", 
            "student_id": student.id,
            "message": "Student registered successfully. Login with Roll No as username and password."
        })

    except Classroom.DoesNotExist:
        return JsonResponse({"error": "Invalid Classroom ID"}, status=400)
    except Exception as e:
        print(f"Registration Error: {e}")
        # If user creation failed but not caught specifically, we might want to ensure atomicity handles it.
        # atomic() block ensures if student creation fails, user creation is rolled back.
        return JsonResponse({"error": str(e)}, status=500)

def student_delete_view(request, pk):
    """Deletes a student record."""
    student = get_object_or_404(Student, pk=pk)
    
    if request.method == "POST":
        student.delete()
        return redirect('students:student_list')
        
    return redirect('students:student_list')
