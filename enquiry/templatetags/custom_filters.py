from datetime import timezone
from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    


@register.filter
def div(value, arg):
    try:
        return float(value) / float(arg) if float(arg) != 0 else 0
    except (ValueError, TypeError):
        return ''
    
    



@register.filter
def balance_percentage(fees_paid, target_fees):
    try:
        paid = float(fees_paid) if fees_paid else 0
        total = float(target_fees) if target_fees else 0
        if total == 0:
            return 0
        balance = total - paid
        if balance < 0:
            balance = 0
        percentage = (balance / total) * 100
        return round(percentage, 2)
    except (TypeError, ValueError):
        return 0

@register.filter
def paid_percentage(fees_paid, target_fees):
    try:
        paid = float(fees_paid) if fees_paid else 0
        total = float(target_fees) if target_fees else 0
        if total == 0:
            return 0
        percentage = (paid / total) * 100
        if percentage > 100:
            percentage = 100
        return round(percentage, 2)
    except (TypeError, ValueError):
        return 0
    
    


@register.filter
def split_month(value):
    if not value:
        return {'year': timezone.now().year, 'month': timezone.now().month}
    try:
        year, month = map(int, value.split('-'))
        return {'year': year, 'month': month}
    except:
        return {'year': timezone.now().year, 'month': timezone.now().month}
    
    
@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))




@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''
    
    


@register.filter
def div1(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul1(value, arg):
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0




@register.filter
def add(value, arg):
    try:
        return float(value) + float(arg)
    except ValueError:
        return value