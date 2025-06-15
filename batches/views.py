from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.utils import timezone
from .models import Batch, Trainer, Tracker
from .forms import BatchForm
from enquiry.models import Enquiry

from django.shortcuts import render
from django.utils import timezone
from itertools import groupby
from operator import attrgetter
from calendar import month_name

def batch_list(request):
    # Get today's date
    today = timezone.now().date()
    
    # Get query parameters or default to current month/year
    current_month = int(request.GET.get('month', today.month))
    current_year = int(request.GET.get('year', today.year))
    
    # Calculate next/previous months/years (for navigation)
    prev_month = 12 if current_month == 1 else current_month - 1
    prev_year = current_year - 1 if current_month == 1 else current_year
    next_month = 1 if current_month == 12 else current_month + 1
    next_year = current_year + 1 if current_month == 12 else current_year

    # Query batches for current month/year
    batches = Batch.objects.select_related('trainer', 'tracker') \
        .prefetch_related('students') \
        .filter(batch_date__year=current_year, batch_date__month=current_month) \
        .order_by('batch_date', '-created_at')

    # Group batches by date
    grouped_batches = []
    for key, group in groupby(batches, key=attrgetter('batch_date')):
        grouped_batches.append({
            'date': key,
            'batches': list(group),
        })

    # Generate month/year lists for dropdowns
    months = [{'num': i, 'name': month_name[i]} for i in range(1, 13)]
    years = [y for y in range(2020, today.year + 2)]

    return render(request, 'batches/batch_list.html', {
        'grouped_batches': grouped_batches,
        'months': months,
        'years': years,
        'current_month': current_month,
        'current_year': current_year,
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        'today': today,
        'total_batches': len(batches),
    })
# Create a New Batch
def create_batch(request):
    if request.method == 'POST':
        form = BatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Batch created successfully!")
            return redirect('batch:batch_list')
    else:
        form = BatchForm()

    return render(request, 'batches/create_batch.html', {'form': form})


# Edit Batch Details
def edit_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    form = BatchForm(request.POST or None, instance=batch)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Batch updated successfully.')
        return redirect('batch:batch_detail', batch_id=batch.id)
    return render(request, 'batches/edit_batch.html', {'form': form, 'batch': batch})

from django.shortcuts import render, get_object_or_404
from enquiry.models import Enquiry
from .models import Batch

def batch_detail(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    assigned = batch.students.all()
    unassigned = Enquiry.objects.filter(
        status='joined',
        is_joined_batch=False
    ).exclude(id__in=assigned.values_list('id', flat=True))

    # Per-student and batch total summary
    payment_data = {}
    total_target = 0
    total_paid = 0
    total_balance = 0

    for student in assigned:
        target = student.target_fees or 0
        paid = student.fees_paid or 0
        balance = target - paid

        payment_data[student.id] = {
            'target': target,
            'paid': paid,
            'balance': balance
        }

        total_target += target
        total_paid += paid
        total_balance += balance

    batch_payment_summary = {
        'total_target': total_target,
        'total_paid': total_paid,
        'total_balance': total_balance,
    }

    context = {
        'batch': batch,
        'assigned': assigned,
        'unassigned': unassigned,
        'total': assigned.count(),
        'payment_data': payment_data,
        'batch_payment_summary': batch_payment_summary,
    }

    return render(request, 'batches/batch_detail.html', context)



# Assign Single Enquiry to Batch
def assign_to_batch(request, batch_id, enquiry_id):
    batch = get_object_or_404(Batch, id=batch_id)
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)

    if request.method == 'POST':
        if not batch.students.filter(id=enquiry.id).exists():
            batch.students.add(enquiry)
            enquiry.is_joined_batch = True
            enquiry.save()
            messages.success(request, f"{enquiry.name} assigned to batch {batch.code}.")
        else:
            messages.info(request, f"{enquiry.name} is already in batch {batch.code}.")

    return redirect('batch:batch_detail', batch_id=batch.id)

# views.py

def remove_from_batch(request, batch_id, enquiry_id):
    batch = get_object_or_404(Batch, id=batch_id)
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)

    if request.method == 'POST':
        if batch.students.filter(id=enquiry.id).exists():
            batch.students.remove(enquiry)

            # Refresh the enquiry object to clear cached relationships
            enquiry.refresh_from_db()

            # Now check if the enquiry is in any other batches
            if not enquiry.batches.exists():
                enquiry.is_joined_batch = False
                enquiry.save()
            
            messages.success(request, f'{enquiry.name} removed from batch {batch.code}.')
        else:
            messages.warning(request, f'{enquiry.name} was not assigned to this batch.')

    return redirect('batch:batch_detail', batch_id=batch.id)

# Bulk Assign Enquiries to Batch
def bulk_assign_to_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    if request.method == 'POST':
        enquiry_ids = request.POST.getlist('enquiry_ids')
        added_count = 0
        for enquiry in Enquiry.objects.filter(id__in=enquiry_ids):
            if not batch.students.filter(id=enquiry.id).exists():
                batch.students.add(enquiry)
                enquiry.is_joined_batch = True
                enquiry.save()
                added_count += 1

        messages.success(request, f'{added_count} students assigned to batch {batch.code}.')

    return redirect('batch:batch_detail', batch_id=batch.id)

def bulk_remove_from_batch(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    if request.method == 'POST':
        enquiry_ids = request.POST.getlist('enquiry_ids')
        removed_count = 0
        for enquiry in Enquiry.objects.filter(id__in=enquiry_ids):
            if batch.students.filter(id=enquiry.id).exists():
                batch.students.remove(enquiry)
                enquiry.refresh_from_db()  # Refresh after removal
                if not enquiry.batches.exists():
                    enquiry.is_joined_batch = False
                    enquiry.save()
                removed_count += 1

        messages.success(request, f'{removed_count} students removed from batch {batch.code}.')
    return redirect('batch:batch_detail', batch_id=batch.id)




# views.py
from django.shortcuts import render, get_object_or_404
from .models import Batch

def batch_fee_summary(request, batch_id):
    batch = get_object_or_404(Batch, id=batch_id)
    data = batch.fee_summary()
    return render(request, 'batch_fee_summary.html', {
        'batch': batch,
        'summary': data['summary'],
        'total_target': data['total_target'],
        'total_paid': data['total_paid'],
        'total_balance': data['total_balance'],
    })

