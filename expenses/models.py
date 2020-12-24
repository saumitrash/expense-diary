import datetime
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
        
        day,month,year = now.day, now.month, now.year

        return now - datetime.timedelta(days=day) <= self.payment_time <= now
    
    class Meta:
        ordering = ['-payment_time'] # descending order --> most recent first