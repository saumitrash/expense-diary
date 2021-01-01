from django.test import TestCase
from django.urls import reverse

from datetime import timedelta
from django.utils import timezone
# Create your tests here.

from .models import Expense

truncation = 25 - 1


def add_expense(amount=0, days=0, title="default title", desc="default desc"):
    time = timezone.now() + timedelta(days=days)

    return Expense.objects.create(amount=amount,
                                  payment_time=time,
                                  title=title,
                                  description=desc)


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

        time = now - timedelta(days=(today + 1), seconds=1)

        old_expense = Expense(payment_time=time)

        self.assertIs(old_expense.was_payed_recently(), False)


class ExpenseHomeViewTests(TestCase):
    def test_home_view_redirect(self):
        now = timezone.now()
        month, year = now.month, now.year
        expected_path = '/expense/%d/%d/' % (year, month)
        response = self.client.get(reverse('expenses:home'))
        self.assertRedirects(response,
                             expected_url=expected_path,
                             target_status_code=200,
                             fetch_redirect_response=True)


class ExpenseIndexViewTests(TestCase):
    def test_past_expense_route_edge(self):
        # now = timezone.now()
        # month, year = now.month, now.year
        month, year = 1, 2021
        response = self.client.get(
            reverse('expenses:index', args=(year, month)))
        self.assertEqual(response.context['prev'], {'year': 2020, 'month': 12})

    def test_no_expenses(self):
        """
        If no expenses exist, an appropriate message is displayed.
        """
        now = timezone.now()
        month, year = now.month, now.year
        response = self.client.get(
            reverse('expenses:index', args=(year, month)))
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

        delta_days = -(day + 1)

        add_expense(amount=500, days=delta_days)
        response = self.client.get(
            reverse('expenses:index', args=(year, month)))
        self.assertQuerysetEqual(response.context['page_obj'], [])

    def test_past_expense_on_past_index(self):
        """
        expenses with a payment_date in the past are
        displayed on the past index page if the month if correct.
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year

        delta_days = -(day + 1)

        add_expense(amount=500, days=delta_days)
        old_time = now + timedelta(days=delta_days)
        old_year, old_month = old_time.year, old_time.month

        response = self.client.get(
            reverse('expenses:index', args=(old_year, old_month)))
        self.assertNotContains(response, 'Add Expense')
        self.assertEqual(response.status_code, 200)

        self.assertTrue(len(response.context['page_obj']) == 1)
        self.assertQuerysetEqual(response.context['page_obj'],
                                 ['<Expense: 500.0>'])

    def test_present_expense_with_no_past_expense(self):
        """
        expenses with a payment_date in the past are not
        displayed on the present index page, only the
        present month's expenses should show.
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year

        add_expense(amount=500)

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "badge-expended")
        self.assertContains(response, "more than last month")

        self.assertTrue(len(response.context['page_obj']) == 1)

        self.assertQuerysetEqual(response.context['page_obj'],
                                 ['<Expense: 500.0>'])

    def test_present_expense_with_more_past_expense(self):
        """
        Less expense in the present month compared to last month
        display a badge-saved, and text related to badge-saved
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year

        add_expense(amount=500)
        add_expense(amount=1000, days=-(day + 1))

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "badge-saved")
        self.assertContains(response, "less than last month")

        self.assertTrue(len(response.context['page_obj']) == 1)

        self.assertQuerysetEqual(response.context['page_obj'],
                                 ['<Expense: 500.0>'])

    def test_present_expense_with_less_past_expense(self):
        """
        More expense in the present month compared to last month
        display a badge-expended, and text related to badge-expended
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year

        add_expense(amount=500)
        add_expense(amount=200, days=-(day + 1))

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "badge-expended")
        self.assertContains(response, "more than last month")

        self.assertTrue(len(response.context['page_obj']) == 1)

        self.assertQuerysetEqual(response.context['page_obj'],
                                 ['<Expense: 500.0>'])

    def test_present_expense_with_same_past_expense(self):
        """
        Same expenses in the present and past month should
        display a badge-same, and text related to badge-same
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year

        add_expense(amount=500)
        add_expense(amount=500, days=-(day + 1))

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "badge-same")
        self.assertContains(response, "Same as last month")
        self.assertNotContains(response, "Rs. 0 Same as last month")

        self.assertTrue(len(response.context['page_obj']) == 1)

        self.assertQuerysetEqual(response.context['page_obj'],
                                 ['<Expense: 500.0>'])

    def test_present_expense_with_multiple_expenses_less_than_page_objects(
            self):
        """
        expenses items are less than the paginated items allowed
        on the page, so all of them should be displayed on the page
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year

        for i in range(3):
            add_expense(amount=(500 * (i + 1)))

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "badge-expended")
        self.assertContains(response, "more than last month")

        self.assertTrue(len(response.context['page_obj']) == 3)

        self.assertQuerysetEqual(response.context['page_obj'], [
            repr(x) for x in Expense.objects.filter(payment_time__month=month,
                                                    payment_time__year=year)
        ])

    def test_present_expense_with_multiple_expenses_more_than_page_objects(
            self):
        """
        expenses items should not exceed the paginated items allowed
        on the page
        """
        now = timezone.now()
        day, month, year = now.day, now.month, now.year

        for _ in range(7):
            add_expense(amount=500)

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "badge-expended")
        self.assertContains(response, "more than last month")

        self.assertTrue(len(response.context['page_obj']) == 6)

        self.assertQuerysetEqual(response.context['page_obj'], [
            repr(x)
            for x in Expense.objects.filter(payment_time__month=month,
                                            payment_time__year=year)[:6]
        ])

    def test_expense_intcomma(self):
        now = timezone.now()
        year, month = now.year, now.month

        add_expense(amount=40500)

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))
        self.assertContains(response, '40,500.0', count=3)

    def test_expense_intword_million(self):
        now = timezone.now()
        year, month = now.year, now.month

        add_expense(amount=1200000)

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        # count=3, as no expenses in last month so (2 badges, 1 card header)
        self.assertContains(response, '1.2 million', count=3)

    def test_expense_intword_billion(self):
        now = timezone.now()
        year, month = now.year, now.month

        add_expense(amount=1200000000)

        response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        # count=3, as no expenses in last month so (2 badges, 1 card header)
        self.assertContains(response, '1.2 billion', count=3)


class ExpenseDetailViewTests(TestCase):
    def test_detail_no_expenses(self):
        test_id = 1  # number doesn't matter as there is no item yet
        response = self.client.get(reverse('expenses:detail', args=(1, )))
        self.assertEqual(response.status_code, 404)

    def test_detail_expense(self):
        add_expense(amount=1534500, title='Custom Expense Test')

        response = self.client.get(reverse('expenses:detail', args=(1, )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Custom Expense Test')
        self.assertContains(response, '1,534,500', count=1)


class ExpenseDeleteTests(TestCase):
    def test_delete_present_expense(self):
        now = timezone.now()
        year, month = now.year, now.month
        e = add_expense(amount=500)
        add_expense(amount=500)
        add_expense(amount=1000)
        response = self.client.post(
            reverse('expenses:delete_expense', args=(e.id, )))
        self.assertEqual(response.status_code, 302)
        index_response = self.client.get(
            reverse('expenses:index', args=(year, month)))
        self.assertContains(index_response,
                            'Successfully <b>deleted</b> the requested item!')
        self.assertContains(index_response, '1,500.0')


class ExpenseUpdateTests(TestCase):
    def test_update_no_expense(self):
        test_id = 1
        response = self.client.post(
            reverse('expenses:update', args=(test_id, )))
        self.assertEqual(response.status_code, 404)

    def test_update_present_expense(self):
        now = timezone.now()
        year, month = now.year, now.month
        e = add_expense(amount=500)
        add_expense(amount=500)
        add_expense(amount=1000)
        path_to_post = reverse('expenses:update', args=(e.id, ))

        update_title = 'updated test expense title'
        update_desc = 'updated test expense description'

        response = self.client.post(path_to_post,
                                    data={
                                        'price': 1500,
                                        'title': update_title,
                                        'desc': update_desc
                                    })

        self.assertEqual(response.status_code, 302)

        index_response = self.client.get(
            reverse('expenses:index', args=(year, month)))

        self.assertContains(index_response,
                            'Successfully <b>updated</b> the expense!')
        self.assertContains(index_response, '3,000.0')
        self.assertContains(index_response, update_title[:24])  # truncation
        self.assertContains(index_response, update_desc[:24])  # truncation

    def test_update_past_expense(self):
        now = timezone.now()
        year, month, days = now.year, now.month, now.day
        delta_days = -(days + 1)

        old_time = now + timedelta(days=delta_days)

        e = add_expense(amount=500, days=delta_days)
        add_expense(amount=500, days=delta_days)
        add_expense(amount=1000, days=delta_days)

        path_to_post = reverse('expenses:update', args=(e.id, ))

        update_title = 'updated test expense title'
        update_desc = 'updated test expense description'

        response = self.client.post(path_to_post,
                                    data={
                                        'price': 1500,
                                        'title': update_title,
                                        'desc': update_desc
                                    })

        self.assertEqual(response.status_code, 302)

        index_response = self.client.get(
            reverse('expenses:index', args=(old_time.year, old_time.month)))

        self.assertContains(index_response,
                            'Successfully <b>updated</b> the expense!')
        self.assertContains(index_response, '3,000.0')
        self.assertContains(index_response, update_title[:24])  # truncation
        self.assertContains(index_response, update_desc[:24])  # truncation


# Remaining ------------------------
# tests for --> monthly chart (GET)
