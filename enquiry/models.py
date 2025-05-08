from django.db import models

class Counsellor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    mobile = models.CharField(max_length=15)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Enquiry(models.Model):
    STATUS_CHOICES = [
        ('joined', 'Joined'),
        ('pending', 'Pending'),
        ('dropout', 'Dropout'),
    ]

    SUBJECT_CHOICES = [
        ('java_full_stack', 'Java Full Stack'),
        ('python_full_stack', 'Python Full Stack'),
        ('other', 'Other'),
    ]

    ENQUIRY_TYPE_CHOICES = [
        ('someone', 'Enquiry for Someone'),
        ('direct', 'Direct Enquiry'),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    enquiry_type = models.CharField(max_length=10, choices=ENQUIRY_TYPE_CHOICES, default='direct')  # New field
    counsellor = models.ForeignKey(Counsellor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    followup_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.mobile}"



from django.utils import timezone

class Comment(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # Change this line
    class Meta:
        get_latest_by = 'created_at'  # Add this line
        ordering = ['-created_at']    # And this line

  

    def __str__(self):
        return f"Comment by {self.author} on {self.created_at}"