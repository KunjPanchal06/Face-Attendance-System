from students.models import Student
from attendance.models import Attendance

def verify():
    print("Verifying data...")
    kunj = Student.objects.filter(full_name__icontains='Kunj').first()
    yagnik = Student.objects.filter(full_name__icontains='Yagnik').first()

    if kunj:
        recs = Attendance.objects.filter(student=kunj).order_by('timestamp')
        print(f"Kunj Records: {[r.timestamp.date() for r in recs]}")

    if yagnik:
        recs = Attendance.objects.filter(student=yagnik).order_by('timestamp')
        print(f"Yagnik Records: {[r.timestamp.date() for r in recs]}")

if __name__ == '__main__':
    verify()
