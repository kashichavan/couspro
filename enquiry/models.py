from django.db import models
from django.core.exceptions import ValidationError

class Counsellor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    mobile = models.CharField(max_length=15)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


from django.db import models

from django.db import models
from django.core.exceptions import ValidationError

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
        ('someone_telephonic', 'Enquiry for Someone Telephonic'),
        ('direct_telephonic', 'Direct Enquiry Telephonic'),
        ('someone_walkin', 'Enquiry for Someone WalkIn'),
        ('direct_walkin', 'Direct Enquiry WalkIn'),
        ('telephonic_to_walkin','Telephonic To Walkin'),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15,unique=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    enquiry_type = models.CharField(max_length=30, choices=ENQUIRY_TYPE_CHOICES, default='direct_telephonic')
    counsellor = models.ForeignKey('Counsellor', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    followup_date = models.DateField(null=True, blank=True)
    enquiry_date = models.DateField(null=True, blank=True)
    
    parent_number=models.CharField(max_length=15,blank=True,null=True)

    target_fees = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text="Total fees for the course"
    )
    fees_paid = models.DecimalField(
        max_digits=12, decimal_places=2,
        default=0.00,
        help_text="Total amount paid by the student"
    )
    fees_balance = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        help_text="Remaining balance (calculated automatically)"
    )
    due_date = models.DateField(
        null=True, blank=True,
        help_text="Deadline for full fees payment"
    )

    def clean(self):
        if self.target_fees is not None and self.fees_paid > self.target_fees:
            raise ValidationError("Fees paid cannot exceed target fees.")

    def save(self, *args, **kwargs):
        # Calculate balance before saving
        if self.target_fees is not None:
            self.fees_balance = max(self.target_fees - self.fees_paid, 0)
        else:
            self.fees_balance = None
        # Run validations
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_fully_paid(self):
        return self.target_fees is not None and self.fees_paid >= self.target_fees




from django.utils import timezone

class Comment(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)  # Change this line
    class Meta:
        get_latest_by = 'created_at'  # Add this line
        ordering = ['-created_at']    # And this line

  

    def __str__(self):
        return f"Comment  on {self.created_at}"