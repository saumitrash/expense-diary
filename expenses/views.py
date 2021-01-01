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

    return HttpResponseRedirect(reverse('expenses:index', args=(
        year,
        month,
    )))


def index(request, year_num, month_num):
    this_time = timezone.now()
    this_day, this_month, this_year = this_time.day, this_time.month, this_time.year

    requested_expenses = Expense.objects.filter(payment_time__month=month_num,
                                                payment_time__year=year_num)

    paginator = Paginator(requested_expenses, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    requested_monthly_expense = sum(
        [expense.amount for expense in requested_expenses])

    show_add_button = False

    # captured_date = datetime(year=year_num,
    #                          month=month_num,
    #                          day=1,
    #                          tzinfo=timezone.get_current_timezone())
    captured_date = datetime(year=year_num,
                             month=month_num,
                             day=1,
                             tzinfo=timezone.utc)


    if this_time - timedelta(days=this_day) <= captured_date <= this_time:
        show_add_button = True

    prev_exp_month = month_num - 1
    prev_exp_year = year_num

    if prev_exp_month == 0:
        prev_exp_month = 12
        prev_exp_year -= 1

    prev = {'month': prev_exp_month, 'year': prev_exp_year}

    last_monthly_expense = Expense.objects.filter(
        payment_time__month=prev_exp_month,
        payment_time__year=prev_exp_year).aggregate(
            Sum('amount'))['amount__sum']

    if not last_monthly_expense:
        last_monthly_expense = 0

    progress = {}
    progress['color'] = {}
    if requested_monthly_expense > last_monthly_expense:
        progress['color']['bg'] = 'expended'
        progress['color']['text'] = 'light'
        progress['tail'] = 'more than'
    elif requested_monthly_expense < last_monthly_expense:
        progress['color']['bg'] = 'saved'
        progress['color']['text'] = 'dark'
        progress['tail'] = 'less than'
    else:
        progress['color']['bg'] = 'same'
        progress['color']['text'] = 'light'
        progress['tail'] = 'Same as'

    progress['tail'] += ' last month'
    progress['difference'] = abs(requested_monthly_expense -
                                 last_monthly_expense)

    data = {
        # 'expenses': curr_expenses,
        'prev': prev,
        'curr_monthly_expense': requested_monthly_expense,
        'last_monthly_expense': last_monthly_expense,
        'progress': progress,
        'show_add_button': show_add_button,
        'captured_date': captured_date,
        'page_obj': page_obj
    }
    return render(request, 'expenses/index.html', context=data)


def detail(request, expense_id):
    expense_object = get_object_or_404(Expense, id=expense_id)
    data = {'expense': expense_object}
    return render(request, 'expenses/detail.html', context=data)


def add_expense(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        desc = request.POST.get('desc')
        price = float(request.POST.get('price'))

        new_expense = Expense(title=title,
                              description=desc,
                              amount=price,
                              payment_time=timezone.now())

        new_expense.save()

        messages.add_message(request,
                             level=SUCCESS,
                             message='Successfully <b>added</b> the expense!',
                             extra_tags='safe')

        return HttpResponseRedirect(reverse('expenses:home'))

    return render(request, 'expenses/add_expense.html')


def delete_expense(request, expense_id):
    if request.method == 'POST':
        expense = get_object_or_404(Expense, id=expense_id)
        expense_time = expense.payment_time
        month, year = expense_time.month, expense_time.year

        expense.delete()

        messages.add_message(
            request,
            level=SUCCESS,
            message='Successfully <b>deleted</b> the requested item!',
            extra_tags='safe')

        return HttpResponseRedirect(
            reverse('expenses:index', args=(year, month)))

    else:
        messages.add_message(request,
                             level=messages.ERROR,
                             message='Invalid request to delete an item!',
                             extra_tags='safe')

        return HttpResponseRedirect(reverse('expenses:home'))


def update_expense(request, expense_id):
    if request.method == 'POST':
        expense = get_object_or_404(Expense, id=expense_id)
        title = request.POST.get('title')
        description = request.POST.get('desc')
        amount = request.POST.get('price')

        expense_time = expense.payment_time
        year, month = expense_time.year, expense_time.month

        if title:
            expense.title = title
        if description:
            expense.description = description
        if amount:
            expense.amount = amount

        expense.save()

        messages.add_message(
            request,
            level=SUCCESS,
            message='Successfully <b>updated</b> the expense!',
            extra_tags='safe')

        return HttpResponseRedirect(
            reverse('expenses:index', args=(
                year,
                month,
            )))

    expense = get_object_or_404(Expense, id=expense_id)

    return render(request, 'expenses/update_expense.html', {
        'expense': expense,
    })


def monthly_chart(request, year_num, month_num):
    labels = []
    data = []

    expenses_list = Expense.objects.values('payment_time__day')\
        .order_by('payment_time__day')\
        .annotate(total_expenses=Sum('amount'))\
        .filter(
            payment_time__month=month_num,
            payment_time__year=year_num
        )

    for expense in expenses_list:
        expense_day = expense.get('payment_time__day')
        expense_date = datetime(year=year_num, month=month_num, day=expense_day)
        labels.append(expense_date)
        data.append(expense.get('total_expenses'))

    return render(
        request, 'expenses/month_chart.html', {
            'labels': labels,
            'data': data,
            'req_date': datetime(year=year_num, month=month_num, day=1)
        })


def delete_expenses_monthly(request, year_num, month_num):
    if request.method == 'POST':
        expenses = get_list_or_404(Expense,
                                   payment_time__month=month_num,
                                   payment_time__year=year_num)

        for expense in expenses:
            expense.delete()

        messages.add_message(
            request,
            level=SUCCESS,
            message=
            'Successfully <b>deleted</b> all of the expense in the requested month!',
            extra_tags='safe')

        return HttpResponseRedirect(
            reverse('expenses:index', args=(year_num, month_num)))

    else:
        messages.add_message(request,
                             level=messages.ERROR,
                             message='Invalid request to delete items!',
                             extra_tags='safe')

        return HttpResponseRedirect(
            reverse('expenses:index', args=(year_num, month_num)))
