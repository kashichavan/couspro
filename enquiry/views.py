from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from datetime import datetime, date, timedelta
import pytz
import calendar
from django.views.generic import ListView

from .forms import EnquiryForm, CounsellorForm
from .models import Enquiry, Comment



# Indian Standard Time configuration
IST = pytz.timezone('Asia/Kolkata')

def get_ist_time():
    """Return current datetime in IST"""
    return datetime.now(IST)

def home(request):
    now_ist = get_ist_time()
    today = now_ist.date()
    
    pending_count = Enquiry.objects.filter(status='pending').count()
    joined_count = Enquiry.objects.filter(status='joined').count()
    dropout_count = Enquiry.objects.filter(status='dropout').count()
    today_followup_count = Enquiry.objects.filter(followup_date=today, status='pending').count()
    
    recent_enquiries = Enquiry.objects.all().order_by('-created_at')[:5]
    
    next_week = today + timedelta(days=7)
    upcoming_followups = Enquiry.objects.filter(
        followup_date__gte=today,
        followup_date__lte=next_week,
        status='pending'
    ).order_by('followup_date')[:5]
    
    total_count = max(pending_count + joined_count + dropout_count, 1)
    pending_percentage = int((pending_count / total_count) * 200)
    joined_percentage = int((joined_count / total_count) * 200)
    dropout_percentage = int((dropout_count / total_count) * 200)
    
    context = {
        'pending_count': pending_count,
        'joined_count': joined_count,
        'dropout_count': dropout_count,
        'today_followup_count': today_followup_count,
        'recent_enquiries': recent_enquiries,
        'upcoming_followups': upcoming_followups,
        'pending_percentage': pending_percentage,
        'joined_percentage': joined_percentage,
        'dropout_percentage': dropout_percentage,
    }
    
    return render(request, 'home.html', context)

def enquiry_success(request):
    return HttpResponse('Enquiry added successfully!')

def counsellor_success(request):
    return HttpResponse('Counsellor added successfully!')

def add_enquiry(request):
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('enquiry:dashboard')
    else:
        form = EnquiryForm()
    return render(request, 'add_enquiry.html', {'form': form})

def add_counsellor(request):
    if request.method == 'POST':
        form = CounsellorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('enquiry:counsellor_success')
    else:
        form = CounsellorForm()
    return render(request, 'add_counsellor.html', {'form': form})

def today_followups(request):
    today = get_ist_time().date()
    enquiries = Enquiry.objects.filter(followup_date=today, status='pending')
    return render(request, 'today_followups.html', {'enquiries': enquiries, 'today': today})

# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Enquiry, Comment

@require_POST
def add_comment(request):
    try:
        enquiry_id = request.POST.get('enquiry_id')
        comment_text = request.POST.get('comment')
        
        if not enquiry_id or not comment_text:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required parameters'
            }, status=400)
            
        enquiry = Enquiry.objects.get(id=enquiry_id)
        comment = Comment.objects.create(
            enquiry=enquiry,
            comment=comment_text,
        )
        
        return JsonResponse({
            'status': 'success',
            'truncated_comment': comment.comment[:40] + ('...' if len(comment.comment) > 40 else '')
        })
        
    except Enquiry.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Enquiry not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def update_followup_date(request):
    if request.method == 'POST':
        enquiry_id = request.POST.get('enquiry_id')
        new_date = request.POST.get('followup_date')

        try:
            enquiry = Enquiry.objects.get(id=enquiry_id)
            enquiry.followup_date = new_date
            enquiry.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def update_comment(request):
    if request.method == "POST":
        enquiry_id = request.POST.get("enquiry_id")
        new_comment = request.POST.get("comment")

        try:
            enquiry = Enquiry.objects.get(id=enquiry_id)
            enquiry.comment = new_comment
            enquiry.save()
            return JsonResponse({'status': 'success'})
        except Enquiry.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Enquiry not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def get_comments(request):
    enquiry_id = request.GET.get('enquiry_id')
    enquiry = Enquiry.objects.get(id=enquiry_id)
    comments = enquiry.comments.all().order_by('-created_at')
    return render(request, 'comments_partial.html', {'comments': comments})

def update_status(request):
    if request.method == 'POST':
        enquiry_id = request.POST.get('enquiry_id')
        new_status = request.POST.get('new_status')
        
        try:
            enquiry = Enquiry.objects.get(id=enquiry_id)
            enquiry.status = new_status
            enquiry.save()
            return JsonResponse({
                'status': 'success',
                'message': 'Status updated successfully',
                'new_status_display': enquiry.get_status_display(),
                'new_status': new_status
            })
        except Enquiry.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Enquiry not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
def joined_students(request):
    students = Enquiry.objects.filter(status='joined').order_by('-created_at')
    return render(request, 'joined_students.html', {'students': students})

def dropout_students(request):
    students = Enquiry.objects.filter(status='dropout').order_by('-created_at')
    return render(request, 'dropout_students.html', {'students': students})

def pending_enquiries(request):
    enquiries = Enquiry.objects.filter(status='pending').order_by('-followup_date')
    return render(request, 'pending_enquiries.html', {'enquiries': enquiries})

def dashboard(request):
    now_ist = get_ist_time()
    today = now_ist.date()
    current_month = now_ist.month
    current_year = now_ist.year
    current_day = now_ist.day

    pending_count = Enquiry.objects.filter(status='pending').count()
    joined_count = Enquiry.objects.filter(status='joined').count()
    dropout_count = Enquiry.objects.filter(status='dropout').count()
    total_enquiries = pending_count + joined_count + dropout_count

    max_height = 200
    pending_percentage = (pending_count / total_enquiries * max_height) if total_enquiries else 0
    joined_percentage = (joined_count / total_enquiries * max_height) if total_enquiries else 0
    dropout_percentage = (dropout_count / total_enquiries * max_height) if total_enquiries else 0

    today_followup_count = Enquiry.objects.filter(followup_date=today).count()
    recent_enquiries = Enquiry.objects.order_by('-created_at')[:10]
    
    next_week = today + timedelta(days=7)
    upcoming_followups = Enquiry.objects.filter(
        followup_date__gte=today,
        followup_date__lte=next_week,
        status='pending'
    ).order_by('followup_date')[:10]

    cal = calendar.monthcalendar(current_year, current_month)
    month_name = calendar.month_name[current_month]
    weekday_names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    followup_dates = list(Enquiry.objects.filter(
        followup_date__year=current_year,
        followup_date__month=current_month
    ).values_list('followup_date__day', flat=True).distinct())

    context = {
        'pending_count': pending_count,
        'joined_count': joined_count,
        'dropout_count': dropout_count,
        'total_enquiries': total_enquiries,
        'today_followup_count': today_followup_count,
        'pending_percentage': pending_percentage,
        'joined_percentage': joined_percentage,
        'dropout_percentage': dropout_percentage,
        'recent_enquiries': recent_enquiries,
        'upcoming_followups': upcoming_followups,
        'calendar_data': cal,
        'month_name': month_name,
        'current_year': current_year,
        'current_month': current_month,
        'current_day': current_day,
        'followup_dates': followup_dates,
        'weekday_names': weekday_names,
    }

    return render(request, 'dashboard.html', context)

def get_calendar_data(request):
    now_ist = get_ist_time()
    month = int(request.GET.get('month', now_ist.month))
    year = int(request.GET.get('year', now_ist.year))
    
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    current_day = now_ist.day if (now_ist.month == month and now_ist.year == year) else None
    
    followup_dates = Enquiry.objects.filter(
        followup_date__year=year,
        followup_date__month=month
    ).values_list('followup_date__day', flat=True).distinct()
    
    calendar_data = []
    for week in cal:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append({'day': '', 'is_today': False, 'has_events': False})
            else:
                week_data.append({
                    'day': day,
                    'is_today': day == current_day,
                    'has_events': day in followup_dates
                })
        calendar_data.append(week_data)
    
    today = now_ist.date()
    start_date = date(year, month, 1)
    
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    month_followups = Enquiry.objects.filter(
        followup_date__gte=max(start_date, today),
        followup_date__lte=end_date,
        status='pending'
    ).order_by('followup_date')[:10]
    
    followups_data = []
    for followup in month_followups:
        followups_data.append({
            'name': followup.name,
            'course': followup.course.name if hasattr(followup.course, 'name') else str(followup.course),
            'date': followup.followup_date.strftime('%Y-%m-%d'),
            'id': followup.id
        })
    
    response_data = {
        'calendar': calendar_data,
        'month_name': month_name,
        'year': year,
        'month': month,
        'followups': followups_data
    }
    
    return JsonResponse(response_data)

def enquiry_details(request, enquiry_id):
    enquiry = get_object_or_404(Enquiry, id=enquiry_id)
    comments = enquiry.comments.all()
    return render(request, 'enquiry_details.html', {'enquiry': enquiry, 'comments': comments})

class EnquiryListView(ListView):
    model = Enquiry
    template_name = 'enquiry_list.html'
    context_object_name = 'enquiries'
    
    def get_queryset(self):
        return Enquiry.objects.select_related('counsellor').prefetch_related('comments').all()
    
# views.py
import openpyxl
from datetime import datetime
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Enquiry, Counsellor
from .forms import BulkEnquiryForm

def download_dummy_template(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    
    # Headers with correct choice values
    headers = [
        'Name', 
        'Mobile', 
        'Subject (java_full_stack/python_full_stack/other)',
        'Status (joined/pending/dropout)', 
        'Enquiry Type (someone/direct)',
        'Counsellor Name', 
        'Followup Date (DD-MM-YYYY)'
    ]
    ws.append(headers)
    
    # Example data with correct values
    example_data = [
        'John Doe', 
        '9876543210', 
        'java_full_stack', 
        'pending', 
        'direct',
        'Counsellor Name', 
        datetime.now().strftime('%d-%m-%Y')
    ]
    ws.append(example_data)
    
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="enquiry_template.xlsx"'
    wb.save(response)
    return response

def bulk_enquiry_upload(request):
    if request.method == 'POST':
        form = BulkEnquiryForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                wb = openpyxl.load_workbook(request.FILES['excel_file'])
                ws = wb.active
                created_count = 0
                errors = []
                
                valid_subjects = dict(Enquiry.SUBJECT_CHOICES).keys()
                valid_statuses = dict(Enquiry.STATUS_CHOICES).keys()
                valid_enquiry_types = dict(Enquiry.ENQUIRY_TYPE_CHOICES).keys()

                for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
                    try:
                        if not any(row):
                            continue

                        # Normalize and validate subject
                        subject = str(row[2]).strip().lower().replace(' ', '_').replace('-', '_') if row[2] else ''
                        if not subject or subject not in valid_subjects:
                            raise ValueError(f"Invalid subject: {row[2]}. Valid options: {', '.join(valid_subjects)}")

                        # Normalize and validate status
                        status = 'pending'  # default
                        if row[3]:
                            status = str(row[3]).strip().lower().replace(' ', '_').replace('-', '_')
                        if status not in valid_statuses:
                            raise ValueError(f"Invalid status: {row[3]}. Valid options: {', '.join(valid_statuses)}")

                        # Normalize and validate enquiry type
                        enquiry_type = 'direct'  # default
                        if row[4]:
                            enquiry_type = str(row[4]).strip().lower().replace(' ', '_').replace('-', '_')
                        if enquiry_type not in valid_enquiry_types:
                            raise ValueError(f"Invalid enquiry type: {row[4]}. Valid options: {', '.join(valid_enquiry_types)}")

                        # Date parsing
                        followup_date = None
                        if row[6]:
                            if isinstance(row[6], datetime):
                                followup_date = row[6].date()
                            else:
                                try:
                                    followup_date = datetime.strptime(str(row[6]), "%d-%m-%Y").date()
                                except ValueError:
                                    raise ValueError("Invalid date format. Use DD-MM-YYYY")

                        # Case-insensitive counsellor lookup
                        counsellor_name = str(row[5]).strip() if row[5] else ''
                        if not counsellor_name:
                            raise ValueError("Counsellor name is required")
                        try:
                            counsellor = Counsellor.objects.get(name__iexact=counsellor_name)
                        except Counsellor.DoesNotExist:
                            raise ValueError(f"Counsellor not found: {counsellor_name}")

                        Enquiry.objects.create(
                            name=row[0],
                            mobile=row[1],
                            subject=subject,
                            status=status,
                            enquiry_type=enquiry_type,
                            counsellor=counsellor,
                            followup_date=followup_date
                        )
                        created_count += 1
                        
                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                
                messages.success(request, f"Successfully created {created_count} enquiries!")
                if errors:
                    messages.error(request, "Errors occurred:\n" + "\n".join(errors))
                
                return redirect('bulk_enquiry_upload')
                
            except Exception as e:
                messages.error(request, f"Error processing file: {str(e)}")
    else:
        form = BulkEnquiryForm()
    
    return render(request, 'bulk_upload.html', {'form': form})