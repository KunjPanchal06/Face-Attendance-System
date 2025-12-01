from django.shortcuts import render, redirect, get_object_or_404
from .models import Classroom

# Create your views here.

def classroom_list(request):
    classrooms = Classroom.objects.all()
    return render(request, 'classrooms/classroom_list.html', 
                  {'classrooms': classrooms,
                   'total_classrooms': classrooms.count()
                })

def classroom_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        capacity = request.POST.get('capacity', 0)

        Classroom.objects.create(name=name, description=description, capacity=capacity)
        return redirect('classroom_list')
    
    return render(request, 'classrooms/classroom_create.html')

def classroom_edit(request, id):
    classroom = get_object_or_404(Classroom, id=id)

    if request.method == 'POST':
        classroom.name = request.POST['name']
        classroom.description = request.POST.get('description', '')
        classroom.capacity = request.POST.get('capacity', 0)
        classroom.save()
        return redirect('classroom_list')

    return render(request, 'classrooms/classroom_edit.html', {'classroom': classroom})

def classroom_delete(request, id):
    classroom = get_object_or_404(Classroom, id=id)
    classroom.delete()
    return redirect('classroom_list')