from django.contrib.messages.constants import SUCCESS
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Sum

from datetime import datetime, timedelta
from calendar import monthrange
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import get_list_or_404, get_object_or_404, render
from .models import Expense
from django.utils import timezone


# Create your views here.

def home(request):
    now = timezone.now()
    year, month = now.year, now.month

    return HttpResponseRedirect(reverse('expenses:index', args=(year,month,)))

def index(request, year_num, month_num):
    this_time = timezone.now()
    this_day, this_month, this_year = this_time.day, this_time.month, this_time.year

    days_in_this_month = monthrange(this_time.year, this_time.month)[1]
    
    curr_expenses = Expense.objects.filter(
        payment_time__month=month_num,
        payment_time__year=year_num
        )

    curr_monthly_expense = sum([expense.amount for expense in curr_expenses])

    paginator = Paginator(curr_expenses, 3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    last_month_expenses = Expense.objects.filter(
        payment_time__month=month_num-1,
        payment_time__year=year_num
        )

    show_add_button = False

    captured_date = datetime(
        year=year_num,
        month=month_num,
        day=this_day,
        tzinfo=timezone.get_current_timezone()
        )

    # if this_time - timedelta(days=days_in_this_month) <= approx_date <= this_time:
    if this_time - timedelta(days=this_day) <= captured_date <= this_time:
        show_add_button = True


    last_monthly_expense = sum([expense.amount for expense in last_month_expenses])

    progress = {}
    progress['color'] = {}
    if curr_monthly_expense > last_monthly_expense:
        progress['color']['bg'] = 'expended'
        progress['color']['text'] = 'light'
        progress['tail'] = 'more than'
    elif curr_monthly_expense < last_monthly_expense:
        progress['color']['bg'] = 'saved'
        progress['color']['text'] = 'dark'
        progress['tail'] = 'less than'
    else:
        progress['color']['bg'] = 'same'
        progress['color']['text'] = 'light'
        progress['tail'] = 'Same as'
    
    progress['tail'] += ' last month'
    progress['difference'] = abs(curr_monthly_expense-last_monthly_expense)

    data = {
        # 'expenses': curr_expenses,
        'curr_monthly_expense': curr_monthly_expense,
        'last_monthly_expense': last_monthly_expense,
        'progress': progress,
        'show_add_button': show_add_button,
        'captured_date': captured_date,
        'page_obj': page_obj
    }
    return render(request, 'expenses/index.html', context=data)


def detail(request, expense_id):
    expense_object = get_object_or_404(Expense, id=expense_id)
    data = {
        'expense': expense_object
    }
    return render(request, 'expenses/detail.html', context=data)


def add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        price = float(request.POST.get('price'))

        new_expense = Expense(title=title, description=desc, amount=price, payment_time=timezone.now())
        
        new_expense.save()

        messages.add_message(request, level=SUCCESS, message='Successfully <b>added</b> the expense!', extra_tags='safe')
    
        return HttpResponseRedirect(reverse('expenses:home'))
    
    return render(request, 'expenses/add_expense.html')


def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id)
    expense.delete()
    
    messages.add_message(request, level=SUCCESS, message='Successfully <b>deleted</b> the expense!', extra_tags='safe')

    return HttpResponseRedirect(reverse('expenses:home'))


def update_expense(request, expense_id):
    if request.method == 'POST':
        expense = get_object_or_404(Expense, id=expense_id)
        title = request.POST.get('title')
        description = request.POST.get('desc')
        amount = request.POST.get('price')

        if title:
            expense.title = title
        if description:
            expense.description = description
        if amount:
            expense.amount = amount

        expense.save()

        messages.add_message(request, level=SUCCESS, message='Successfully <b>updated</b> the expense!', extra_tags='safe')

        return HttpResponseRedirect(reverse('expenses:home'))
    
    expense = get_object_or_404(Expense, id=expense_id)

    return render (request, 'expenses/update_expense.html', {
        'expense': expense,
    })


def monthly_chart(request, year_num, month_num):
    # curr_expenses = get_list_or_404(Expense,
    #     payment_time__month=month_num,
    #     payment_time__year=year_num
    #     )

    labels = []
    data = []

    expenses_list = Expense.objects.values('payment_time__date').annotate(total_price=Sum('amount')).filter(
        payment_time__month=month_num,
        payment_time__year=year_num
        )
    
    for expense in expenses_list:
        labels.append(expense.get('payment_time__date'))
        data.append(expense.get('total_price'))
    
    return render(request, 'expenses/month_chart.html', {
        'labels': labels,
        'data': data,
        'req_date': datetime(year=year_num, month=month_num, day=1)
    })
    

