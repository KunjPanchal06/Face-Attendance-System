"""
Script to clean up duplicate attendance records.
Keeps only the first attendance record per student per day.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'face_attendance.settings')
django.setup()

from attendance.models import Attendance
from collections import defaultdict

def cleanup_duplicates():
    print("Cleaning up duplicate attendance records...")
    
    # Get all records
    records = Attendance.objects.all().order_by('id')
    
    # Group by (student, classroom, date)
    groups = defaultdict(list)
    for record in records:
        key = (record.student_id, record.classroom_id, record.timestamp.date())
        groups[key].append(record)
    
    # Delete duplicates (keep the first one)
    deleted_count = 0
    for key, items in groups.items():
        if len(items) > 1:
            # Keep first, delete rest
            for duplicate in items[1:]:
                print(f"  Deleting duplicate: ID {duplicate.id}, Student {duplicate.student.roll_no}, Date {duplicate.timestamp.date()}")
                duplicate.delete()
                deleted_count += 1
    
    print(f"\nDeleted {deleted_count} duplicate records.")
    print(f"Remaining records: {Attendance.objects.count()}")

if __name__ == '__main__':
    cleanup_duplicates()
