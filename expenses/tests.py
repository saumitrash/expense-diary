from django.test import TestCase
from django.urls import reverse

from datetime import timedelta
from django.utils import timezone
from calendar import monthrange
# Create your tests here.

from .models import Expense


def add_expense(amount=0, days=0, title="default title"):
    time = timezone.now() + timedelta(days=days)
    
    return Expense.objects.create(amount=amount, payment_time=time, title=title)


class ExpenseModelTests(TestCase):

    def test_was_published_recently_with_future_expense(self):
        """
        was_published_recently() returns False for expenses whose pub_date
        is in the future.
        """
        time = timezone.now() + timedelta(days=30)
        future_expense = Expense(payment_time=time)

        self.assertIs(future_expense.was_payed_recently(), False)
    

    def test_was_published_recently_with_old_expense(self):
        """
        was_payed_recently() returns False for expenses whose payment_time
        is older than 1 month(dynamically).
        """
        now = timezone.now()
        today = now.day

        time = now - timedelta(days=(today+1), seconds=1)
        
        old_expense = Expense(payment_time=time)
        
        self.assertIs(old_expense.was_payed_recently(), False)


class ExpenseHomeViewTests(TestCase):
    def test_home_view_redirect(self):
        now = timezone.now()
        month,year = now.month, now.year
        expected_path = '/expense/%d/%d/' % (year, month)
        response = self.client.get(reverse('expenses:home'))
        self.assertRedirects(response, expected_url=expected_path,\
            target_status_code=200, fetch_redirect_response=True)
        

class ExpenseIndexViewTests(TestCase):
    def test_no_expenses(self):
        """
        If no expenses exist, an appropriate message is displayed.
        """
        now = timezone.now()
        month, year = now.month, now.year
        response = self.client.get(reverse('expenses:index', args=(year,month)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No expenses were found")
        self.assertQuerysetEqual(response.context['page_obj'], [])
    
    def test_past_expense_on_present_index(self):
        """
        expenses with a payment_date in the past are not
        displayed on the index page.
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year
        
        delta_days = -(day+1)
        
        add_expense(amount=500, days=delta_days)
        response = self.client.get(reverse('expenses:index', args=(year, month)))
        self.assertQuerysetEqual(
            response.context['page_obj'],
            []
        )
    
    def test_past_expense_on_past_index(self):
        """
        expenses with a payment_date in the past are
        displayed on the past index page if the month if correct.
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year
        
        delta_days = -(day+1)
        
        add_expense(amount=500, days=delta_days)
        response = self.client.get(reverse('expenses:index', args=(year, month-1)))
        self.assertNotContains(response, 'Add Expense')
        self.assertEqual(response.status_code, 200)

        self.assertTrue(len(response.context['page_obj']) == 1)
        self.assertQuerysetEqual(
            response.context['page_obj'],
            ['<Expense: 500.0>']
        )
    
    def test_present_expense_with_no_past_expense(self):
        """
        expenses with a payment_date in the past are not
        displayed on the present index page, only the
        present month's expenses should show.
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year
        
        add_expense(amount=500)

        response = self.client.get(reverse('expenses:index', args=(year, month)))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "badge-expended")
        self.assertContains(response, "more than last month")

        self.assertTrue(len(response.context['page_obj']) == 1)
        
        self.assertQuerysetEqual(
            response.context['page_obj'],
            ['<Expense: 500.0>']
        )

    def test_present_expense_with_more_past_expense(self):
        """
        Less expense in the present month compared to last month
        display a badge-saved, and text related to badge-saved
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year
        
        add_expense(amount=500)
        add_expense(amount=1000, days=-(day+1))

        response = self.client.get(reverse('expenses:index', args=(year, month)))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "badge-saved")
        self.assertContains(response, "less than last month")

        self.assertTrue(len(response.context['page_obj']) == 1)
        
        self.assertQuerysetEqual(
            response.context['page_obj'],
            ['<Expense: 500.0>']
        )
    
    def test_present_expense_with_less_past_expense(self):
        """
        More expense in the present month compared to last month
        display a badge-expended, and text related to badge-expended
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year
        
        add_expense(amount=500)
        add_expense(amount=200, days=-(day+1))

        response = self.client.get(reverse('expenses:index', args=(year, month)))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "badge-expended")
        self.assertContains(response, "more than last month")

        self.assertTrue(len(response.context['page_obj']) == 1)
        
        self.assertQuerysetEqual(
            response.context['page_obj'],
            ['<Expense: 500.0>']
        )
        
    def test_present_expense_with_same_past_expense(self):
        """
        Same expenses in the present and past month should
        display a badge-same, and text related to badge-same
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year
        
        add_expense(amount=500)
        add_expense(amount=500, days=-(day+1))

        response = self.client.get(reverse('expenses:index', args=(year, month)))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "badge-same")
        self.assertContains(response, "Same as last month")

        self.assertTrue(len(response.context['page_obj']) == 1)
        
        self.assertQuerysetEqual(
            response.context['page_obj'],
            ['<Expense: 500.0>']
        )

    def test_present_expense_with_multiple_expenses_less_than_page_objects(self):
        """
        expenses items are less than the paginated items allowed
        on the page, so all of them should be displayed on the page
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year
        
        add_expense(amount=500)
        add_expense(amount=1000)
        add_expense(amount=1500)

        response = self.client.get(reverse('expenses:index', args=(year, month)))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "badge-expended")
        self.assertContains(response, "more than last month")

        self.assertTrue(len(response.context['page_obj']) == 3)

        
        self.assertQuerysetEqual(
            response.context['page_obj'],
            [repr(x) for x in Expense.objects.filter(payment_time__month=month, payment_time__year=year)]
        )
    
    def test_present_expense_with_multiple_expenses_more_than_page_objects(self):
        """
        expenses items should not exceed the paginated items allowed
        on the page
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year
        
        add_expense(amount=500)
        add_expense(amount=500)
        add_expense(amount=500)
        add_expense(amount=500)
        add_expense(amount=500)
        add_expense(amount=500)
        add_expense(amount=500)

        response = self.client.get(reverse('expenses:index', args=(year, month)))
        
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, "badge-expended")
        self.assertContains(response, "more than last month")

        self.assertTrue(len(response.context['page_obj']) == 6)

        
        self.assertQuerysetEqual(
            response.context['page_obj'],
            [repr(x) for x in Expense.objects.filter(payment_time__month=month, payment_time__year=year)[:6]]
        )
    
    
