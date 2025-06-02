from datetime import datetime
import calendar
import pytz

from enquiry.models import MonthlyTarget
from django.utils.timezone import now

def monthly_target_context(request):
    context = {}

    try:
        # Convert current time to IST
        ist = pytz.timezone('Asia/Kolkata')
        today = now().astimezone(ist)
        month = today.month
        year = today.year

        # Get the monthly target (assuming single active target, or filter by user if needed)
        monthly_target = MonthlyTarget.objects.get(
            month=month,
            year=year
        )

        # Calculate date-based metrics
        days_in_month = calendar.monthrange(year, month)[1]
        days_passed = today.day
        days_remaining = days_in_month - days_passed

        # Calculate progress percentage
        if monthly_target.target_amount > 0:
            percentage = (monthly_target.actual_collected / monthly_target.target_amount) * 100
        else:
            percentage = 0

        context['monthly_target'] = {
            'target_amount': monthly_target.target_amount,
            'actual_collected': monthly_target.actual_collected,
            'remaining': monthly_target.target_amount - monthly_target.actual_collected,
            'percentage': round(percentage, 2),
            'days_remaining': days_remaining,
            'days_passed': days_passed,
            'month': monthly_target.get_month_display(),
            'year': monthly_target.year
        }

    except MonthlyTarget.DoesNotExist:
        context['monthly_target'] = None

    return context
