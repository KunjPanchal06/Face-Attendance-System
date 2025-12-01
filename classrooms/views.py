from django.shortcuts import render, redirect, get_object_or_404
from .models import Classroom

# Create your views here.

def classroom_list(request):
    classrooms = Classroom.objects.all()
    return render(request, 'classrooms/list.html', {'classrooms': classrooms})

def classroom_create(request):
    if request.method == 'POST':
        name = request.POST['name']
        description = request.POST.get('description', '')
        Classroom.objects.create(name=name, description=description)
        return redirect('classroom_list')
    
    return render(request, 'classrooms/create.html')

def classroom_edit(request, id):
    classroom = get_object_or_404(Classroom, id=id)

    if request.method == 'POST':
        classroom.name = request.POST['name']
        classroom.description = request.POST.get('description', '')
        classroom.save()
        return redirect('classroom_list')

    return render(request, 'classrooms/edit.html', {'classroom': classroom})

def classroom_delete(request, id):
    classroom = get_object_or_404(Classroom, id=id)
    classroom.delete()
    return redirect('classroom_list')