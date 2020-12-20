from django.urls import path
from . import views

app_name = "expenses"

urlpatterns = [
    path('', views.home, name='home'),
    path('expense/<int:year_num>/<int:month_num>/', views.index, name='index'),
    path('expense/detail/<int:expense_id>/', views.detail, name='detail'),
    path('expense/add/', views.add_expense, name='add'),
    path('expense/update/<int:expense_id>/', views.update_expense, name='update'),
    path('expense/delete/<int:expense_id>', views.delete_expense, name='delete_expense'),
    path('expense/add_expense/', views.add_expense, name='add_expense'),
]