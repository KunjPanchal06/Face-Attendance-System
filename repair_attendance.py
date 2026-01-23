from students.models import Student
from attendance.models import Attendance
from django.utils import timezone
from datetime import timedelta

def repair():
    print("Starting data repair...")
    kunj = Student.objects.filter(full_name__icontains='Kunj').first()
    yagnik = Student.objects.filter(full_name__icontains='Yagnik').first()

    if not kunj or not yagnik:
        print("Could not find students.")
        return

    # Kunj: Needs 2 records. 1 Yesterday, 1 Today.
    kunj_recs = list(Attendance.objects.filter(student=kunj).order_by('id'))
    print(f"Kunj has {len(kunj_recs)} records.")
    
    today = timezone.now()
    yesterday = today - timedelta(days=1)
    
    if len(kunj_recs) >= 2:
        kunj_recs[0].timestamp = yesterday
        kunj_recs[0].save()
        kunj_recs[1].timestamp = today
        kunj_recs[1].save()
        print(f"Fixed Kunj: {yesterday.date()} and {today.date()}")
    elif len(kunj_recs) == 1:
        # Create a second one for yesterday if missing
        Attendance.objects.create(student=kunj, classroom=kunj.classroom, timestamp=yesterday, present=True)
        print("Created missing record for Kunj (Yesterday)")

    # Yagnik: Needs 1 record (Today). Correct.
    yagnik_recs = list(Attendance.objects.filter(student=yagnik).order_by('id'))
    print(f"Yagnik has {len(yagnik_recs)} records.")
    
    if len(yagnik_recs) >= 1:
        yagnik_recs[0].timestamp = today
        yagnik_recs[0].save()
        print(f"Fixed Yagnik: {today.date()}")
        
    print("Repair Complete.")

if __name__ == '__main__':
    repair()
