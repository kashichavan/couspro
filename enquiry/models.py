import calendar
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Counsellor(models.Model):
    name = models.CharField(max_length=100, unique=True)
    mobile = models.CharField(max_length=15)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CollegeInfo(models.Model):
    college_name = models.CharField(max_length=150, unique=True)
    college_place = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return self.college_name


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
        ('telephonic_to_walkin', 'Telephonic To Walkin'),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    enquiry_type = models.CharField(max_length=30, choices=ENQUIRY_TYPE_CHOICES, default='direct_telephonic')
    counsellor = models.ForeignKey(Counsellor, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    followup_date = models.DateField(null=True, blank=True)
    enquiry_date = models.DateField(null=True, blank=True)
    parent_number = models.CharField(max_length=15, blank=True, null=True)
    
    
    fees_paid_date = models.DateField(null=True, blank=True)
    
    native_district_name=models.CharField(max_length=30,blank=True,null=True)

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
    
    
    other_subject_name = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        help_text="Specify the subject if 'Other' is selected"
    )


    college = models.ForeignKey(
        CollegeInfo,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enquiries'
    )

    def clean(self):
        if self.target_fees is not None and self.fees_paid > self.target_fees:
            raise ValidationError("Fees paid cannot exceed target fees.")

    # models.py
    def save(self, *args, **kwargs):
        # Validate other subject
        if self.subject == 'other' and not self.other_subject_name:
            raise ValidationError({
            'other_subject_name': "Please specify the subject when 'Other' is selected."
        })
    
    # Handle fees based on status
        if self.status != 'joined':
            self.target_fees = None
            self.fees_paid = Decimal('0.00')
            self.fees_balance = None
            self.due_date = None
        else:
        # Validate fees
            if self.target_fees is not None and self.fees_paid > self.target_fees:
                raise ValidationError("Fees paid cannot exceed target fees.")
            
        # Calculate balance
            if self.target_fees is not None:
                self.fees_balance = max(self.target_fees - self.fees_paid, Decimal('0.00'))
            else:
                self.fees_balance = None
    
        super().save(*args, **kwargs)

    @property
    def is_fully_paid(self):
        return self.target_fees is not None and self.fees_paid >= self.target_fees
    
    
    VISIT_TYPE_CHOICES = [
        ('alone_walkin', 'Alone Walkin'),
        ('came_with_parents', 'Came with parents'),
        ('student_reference', 'Student Reference'),
        ('old_student_reference', 'Old Student Reference'),
        ('came_with_relatives', 'Came with relatives'),
    ]

    visit_type = models.CharField(
        max_length=30, 
        choices=VISIT_TYPE_CHOICES, 
        default='alone_walkin',
        help_text="How did the student come for enquiry?"
    )


class Comment(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment on {self.created_at}"
    
    
    
    
# models.py
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from .models import Enquiry

class MonthlyTarget(models.Model):
    MONTH_CHOICES = [
        (1, 'January'),
        (2, 'February'),
        (3, 'March'),
        (4, 'April'),
        (5, 'May'),
        (6, 'June'),
        (7, 'July'),
        (8, 'August'),
        (9, 'September'),
        (10, 'October'),
        (11, 'November'),
        (12, 'December'),
    ]

    month = models.PositiveIntegerField(choices=MONTH_CHOICES)
    year = models.PositiveIntegerField(default=timezone.now().year)
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text="Set the monthly fees collection target"
    )

    class Meta:
        unique_together = ('month', 'year')
        verbose_name_plural = "Monthly Targets"

    def __str__(self):
        return f"{calendar.month_name[self.month]} {self.year} - Target: ₹{self.target_amount}"

    @property
    def actual_collected(self):
        from .models import Enquiry

        total = Enquiry.objects.filter(
            fees_paid_date__year=self.year,
            fees_paid_date__month=self.month,
            fees_paid_date__isnull=False
        ).aggregate(Sum('fees_paid'))['fees_paid__sum'] or 0

        return total

    @property
    def remaining(self):
        return max(float(self.target_amount) - float(self.actual_collected), 0)




@receiver(pre_save, sender=Enquiry)
def auto_set_fees_paid_date(sender, instance, **kwargs):
    if instance.fees_paid > 0 and not instance.fees_paid_date:
        instance.fees_paid_date = timezone.now().date()