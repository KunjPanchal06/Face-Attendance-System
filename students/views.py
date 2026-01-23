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
from attendance.models import Attendance

def student_list_view(request):
    """Renders the list of all students."""
    students = Student.objects.select_related('classroom').all()
    classrooms = Classroom.objects.all()
    return render(request, 'students/student_list.html', {'students': students, 'classrooms': classrooms})

def student_detail_view(request, pk):
    """Renders the detailed attendance report for a specific student."""
    student = get_object_or_404(Student, pk=pk)
    
    # Get all attendance records for this student
    present_records = Attendance.objects.filter(student=student)
    # Get the set of timestamps when this student was present
    student_present_timestamps = set(present_records.values_list('timestamp', flat=True))
    present_count = len(student_present_timestamps)
    
    # Get ALL unique session timestamps for this classroom
    # A "session" is defined by a unique timestamp when any student was marked present
    all_session_timestamps = Attendance.objects.filter(
        classroom=student.classroom
    ).values_list('timestamp', flat=True).distinct()
    all_session_timestamps_set = set(all_session_timestamps)
    
    total_sessions = len(all_session_timestamps_set)
    
    # Identify absent sessions (timestamps when student was NOT present)
    absent_timestamps = all_session_timestamps_set - student_present_timestamps
    absent_count = len(absent_timestamps)
    
    # Build combined history list
    history = []
    
    # Add present records
    for record in present_records:
        history.append({
            'date': record.timestamp.date(),
            'time': record.timestamp.strftime('%I:%M %p'),
            'status': 'Present',
            'color': 'green'
        })
        
    # Add absent records
    for timestamp in absent_timestamps:
        history.append({
            'date': timestamp.date(),
            'time': timestamp.strftime('%I:%M %p'),
            'status': 'Absent',
            'color': 'red'
        })
        
    # Sort by date and time descending
    history.sort(key=lambda x: (x['date'], x['time']), reverse=True)
    
    # Avoid division by zero
    attendance_percentage = 0
    if total_sessions > 0:
        attendance_percentage = round((present_count / total_sessions) * 100, 1)
    
    context = {
        'student': student,
        'attendance_history': history,
        'present_count': present_count,
        'total_sessions': total_sessions,
        'absent_count': absent_count,
        'attendance_percentage': attendance_percentage,
    }
    return render(request, 'students/student_detail.html', context)


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
        email = data.get("email", "")  # Get email
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
            # Split name for User model
            names = full_name.split(" ", 1)
            first_name = names[0]
            last_name = names[1] if len(names) > 1 else ""

            # Check if User already exists
            if User.objects.filter(username=roll_no).exists():
                existing_user = User.objects.get(username=roll_no)
                # Check if this user is linked to another student?
                if Student.objects.filter(user=existing_user).exists():
                    return JsonResponse({"error": "A user with this Roll Number already exists and is linked to a student."}, status=400)
                else:
                    # User exists but is orphaned (not linked to any student). 
                    # Likely from a failed previous attempt or deletion without user cleanup.
                    # We can safely delete this orphan user and create a fresh one.
                    existing_user.delete()
            
            # Use roll_no as username and initial password
            user = User.objects.create_user(
                username=roll_no, 
                password=roll_no,
                email=email,
                first_name=first_name,
                last_name=last_name
            )
            
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
        # Delete linked User (which cascades Student delete usually, but we do it explicitly to be safe or if unrelated)
        # Actually, Student -> User is OneToOne on Student side. 
        # If we delete Student, User is NOT deleted by Django default OneToOne unless we set it up that way.
        # But we want to remove the LOGIN account too.
        if student.user:
            student.user.delete() # This might cascade delete the student if on_delete=CASCADE involves it, but let's be sure.
        else:
            student.delete()
            
        return redirect('students:student_list')
        
    return redirect('students:student_list')
