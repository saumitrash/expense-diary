import datetime
from calendar import monthrange
from django.db import models
from django.utils import timezone


# Create your models here.

class Expense(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    amount = models.FloatField()
    payment_time = models.DateTimeField()

    def __str__(self) -> str:
        return str(self.amount)
    
    def was_payed_recently(self):
        now = timezone.now()
        
        # (2,29) --> (weekday of first day of the month, number of days in said month)
        days_in_this_month = monthrange(now.year, now.month)[1]

        return now - datetime.timedelta(days=days_in_this_month) <= self.payment_time <= now