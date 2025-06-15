from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from enquiry.models import Enquiry  # Import from enquiry app

class Trainer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Tracker(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)

    def __str__(self):
        return self.name

from django.db import models

class Batch(models.Model):
    code = models.CharField(max_length=20, unique=True)
    subject = models.CharField(max_length=100)
    trainer = models.ForeignKey(Trainer, on_delete=models.SET_NULL, null=True)
    tracker = models.ForeignKey(Tracker, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True, null=True)
    batch_date = models.DateField(null=True, blank=True)  # 👈 New field
    created_at = models.DateTimeField(auto_now_add=True)
    students = models.ManyToManyField(Enquiry, related_name='batches', blank=True)

    def __str__(self):
        return f"{self.code} ({self.subject})"
    
    
    
    def fee_summary(self):
        students = self.students.all()
        summary = []

        total_target = 0
        total_paid = 0
        total_balance = 0

        for student in students:
            target = student.target_fees or 0
            paid = student.fees_paid or 0
            balance = student.fees_balance or 0

            summary.append({
                'student': student,
                'target_fees': target,
                'fees_paid': paid,
                'fees_balance': balance,
                'is_fully_paid': student.is_fully_paid,
            })

            total_target += target
            total_paid += paid
            total_balance += balance

        return {
            'summary': summary,
            'total_target': total_target,
            'total_paid': total_paid,
            'total_balance': total_balance,
        }
