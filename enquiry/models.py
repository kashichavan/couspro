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

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal

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

    VISIT_TYPE_CHOICES = [
        ('alone_walkin', 'Alone Walkin'),
        ('came_with_parents', 'Came with parents'),
        ('student_reference', 'Student Reference'),
        ('old_student_reference', 'Old Student Reference'),
        ('came_with_relatives', 'Came with relatives'),
        ('telephonic', 'Telephonic'),
    ]

    # 🔹 Basic Info
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True)
    parent_number = models.CharField(max_length=15, blank=True, null=True)
    native_district_name = models.CharField(max_length=30, blank=True, null=True)

    # 🔹 Status & Type
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    other_subject_name = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    enquiry_type = models.CharField(max_length=30, choices=ENQUIRY_TYPE_CHOICES, default='direct_telephonic')
    visit_type = models.CharField(max_length=30, choices=VISIT_TYPE_CHOICES, default='alone_walkin')

    # 🔹 Dates
    created_at = models.DateTimeField(auto_now_add=True)
    followup_date = models.DateField(null=True, blank=True)
    enquiry_date = models.DateField(null=True, blank=True)
    joined_date = models.DateField(null=True, blank=True)
    fees_paid_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)

    # 🔹 Fees
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

    # 🔹 Flags
    is_joined_batch = models.BooleanField(default=False)

    # 🔹 Relationships
    counsellor = models.ForeignKey('Counsellor', on_delete=models.CASCADE, related_name='enquiries')

    def clean(self):
        if self.target_fees is not None and self.fees_paid > self.target_fees:
            raise ValidationError("Fees paid cannot exceed target fees.")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        previous_status = None

        if not is_new:
            try:
                old = Enquiry.objects.get(pk=self.pk)
                previous_status = old.status
            except Enquiry.DoesNotExist:
                previous_status = None

        # Handle joined date
        if previous_status != self.status:
            if self.status == 'joined':
                self.joined_date = timezone.now().date()
            elif self.status == 'dropout':
                if previous_status != 'joined' and not self.joined_date:
                    self.joined_date = timezone.now().date()
            elif self.status == 'pending':
                self.joined_date = None

        # Fees logic
        if self.status != 'joined':
            self.target_fees = None
            self.fees_paid = Decimal('0.00')
            self.fees_balance = None
            self.due_date = None
        else:
            if self.target_fees is not None and self.fees_paid > self.target_fees:
                raise ValidationError("Fees paid cannot exceed target fees.")
            self.fees_balance = (
                self.target_fees - self.fees_paid
                if self.target_fees is not None
                else None
            )

        # Update is_joined_batch flag
        if self.pk and hasattr(self, 'batches') and self.batches.count() > 0:
            self.is_joined_batch = True
        else:
            self.is_joined_batch = False

        super().save(*args, **kwargs)

    @property
    def is_fully_paid(self):
        return self.target_fees is not None and self.fees_paid >= self.target_fees

    def __str__(self):
        return f"{self.name} ({self.mobile})"

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['joined_date']),
            models.Index(fields=['status']),
            models.Index(fields=['counsellor']),
            models.Index(fields=['enquiry_date']),
            models.Index(fields=['enquiry_type']),
        ]
        ordering = ['-created_at']



class Comment(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        get_latest_by = 'created_at'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['enquiry']),
            models.Index(fields=['created_at']),
        ]

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
        from .models import PaymentHistory

        total = PaymentHistory.objects.filter(
            payment_date__year=self.year,
            payment_date__month=self.month
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')

        return total

    @property
    def remaining(self):
        return max(float(self.target_amount) - float(self.actual_collected), 0)




@receiver(pre_save, sender=Enquiry)
def auto_set_fees_paid_date(sender, instance, **kwargs):
    if instance.fees_paid > 0 and not instance.fees_paid_date:
        instance.fees_paid_date = timezone.now().date()
        


# models.py
from django.db import models
from django.utils import timezone

class PaymentHistory(models.Model):
    enquiry = models.ForeignKey('Enquiry', on_delete=models.CASCADE, related_name='payment_history')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.now)
    note = models.CharField(max_length=255, blank=True, null=True)  # optional: "Initial payment", "Partial payment", etc.

    def __str__(self):
        return f"{self.enquiry.name} - ₹{self.amount_paid} on {self.payment_date}"

# enquiry/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Enquiry, PaymentHistory
from django.utils import timezone
from decimal import Decimal
import threading

# Thread-local storage to keep old values
_thread_locals = threading.local()

@receiver(pre_save, sender=Enquiry)
def cache_old_fees_paid(sender, instance, **kwargs):
    """Cache old fees_paid value before saving."""
    if instance.pk:
        try:
            old_instance = Enquiry.objects.get(pk=instance.pk)
            _thread_locals.old_fees_paid = old_instance.fees_paid
        except Enquiry.DoesNotExist:
            _thread_locals.old_fees_paid = Decimal('0.00')
    else:
        # New instance, no old amount
        _thread_locals.old_fees_paid = None

@receiver(post_save, sender=Enquiry)
def log_payment_changes(sender, instance, created, **kwargs):
    """Create PaymentHistory record on new or increased fees_paid."""
    if created:
        if instance.fees_paid > 0:
            PaymentHistory.objects.create(
                enquiry=instance,
                amount_paid=instance.fees_paid,
                payment_date=timezone.now().date()
            )
    else:
        old_amount = getattr(_thread_locals, 'old_fees_paid', None)
        if old_amount is not None:
            new_amount = instance.fees_paid
            if new_amount > old_amount:
                delta = new_amount - old_amount
                PaymentHistory.objects.create(
                    enquiry=instance,
                    amount_paid=delta,
                    payment_date=timezone.now().date()
                )

    # Clean up to avoid leaking thread-local state
    if hasattr(_thread_locals, 'old_fees_paid'):
        del _thread_locals.old_fees_paid


class EducationInfo(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('ug', 'Undergraduate'),
        ('pg', 'Postgraduate'),
    ]

    UG_DEGREE_CHOICES = [
        ('btech', 'B.Tech'),
        ('be', 'B.E'),
        ('bsc', 'B.Sc'),
        ('bca', 'BCA'),
        ('bcom', 'B.Com'),
        ('ba', 'B.A'),
        ('other', 'Other UG'),
    ]

    PG_DEGREE_CHOICES = [
        ('mtech', 'M.Tech'),
        ('mca', 'MCA'),
        ('mba', 'MBA'),
        ('msc', 'M.Sc'),
        ('ma', 'M.A'),
        ('other', 'Other PG'),
    ]

    enquiry = models.ForeignKey('Enquiry', on_delete=models.CASCADE, related_name='education_details')
    level = models.CharField(max_length=2, choices=EDUCATION_LEVEL_CHOICES)

    # Degree choices
    ug_degree = models.CharField(max_length=20, choices=UG_DEGREE_CHOICES, blank=True, null=True)
    other_ug_degree_name = models.CharField(max_length=100, blank=True, null=True)

    pg_degree = models.CharField(max_length=20, choices=PG_DEGREE_CHOICES, blank=True, null=True)
    other_pg_degree_name = models.CharField(max_length=100, blank=True, null=True)

    branch = models.CharField(max_length=100, blank=True, null=True)
    college_name = models.CharField(max_length=200)
    college_place = models.CharField(max_length=200, blank=True, null=True)
    year_of_passing = models.PositiveIntegerField()
    percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="e.g. 78.50")

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.level == 'ug':
            if not self.ug_degree:
                raise ValidationError("UG degree must be selected for undergraduate level.")
            if self.ug_degree == 'other' and not self.other_ug_degree_name:
                raise ValidationError("Please specify the UG degree name when 'Other UG' is selected.")

        elif self.level == 'pg':
            if not self.pg_degree:
                raise ValidationError("PG degree must be selected for postgraduate level.")
            if self.pg_degree == 'other' and not self.other_pg_degree_name:
                raise ValidationError("Please specify the PG degree name when 'Other PG' is selected.")

    def __str__(self):
        degree = ""
        if self.level == 'ug':
            degree = self.other_ug_degree_name if self.ug_degree == 'other' else self.get_ug_degree_display()
        elif self.level == 'pg':
            degree = self.other_pg_degree_name if self.pg_degree == 'other' else self.get_pg_degree_display()

        return f"{self.get_level_display()} - {degree} - {self.college_name} ({self.year_of_passing})"


