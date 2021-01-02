# expense-diary 

A simple Django application to keep track of your monthly expenses. It also provides detailed comparison against expenses in past months.


- [expense-diary](#expense-diary)
  - [Usage](#usage)
    - [Add Expense](#add-expense)
    - [Humanizing expenses](#humanizing-expenses)
    - [Details of an Expense](#details-of-an-expense)
    - [Deleting an Expense](#deleting-an-expense)
    - [Deleting all expenses in a month](#deleting-all-expenses-in-a-month)
    - [Updating an Expense](#updating-an-expense)
    - [Ordering of Expense Items](#ordering-of-expense-items)
    - [Expenses in the past month](#expenses-in-the-past-month)
    - [Visualizing monthly expenses](#visualizing-monthly-expenses)
    - [Expense Badges](#expense-badges)
    - [Pagination](#pagination)
  - [Testing](#testing)
  - [](#)




## Usage

### Add Expense

![](images/annotated/add/add.png)
![](images/annotated/add/add_form.png)
![](images/annotated/add/add_succsess.png)

### Humanizing expenses

For better readability, we "humanize" the large amounts.

![](images/annotated/humanize/add_large.png)
![](images/annotated/humanize/render_large.png)

### Details of an Expense

![](images/annotated/detail/detail.png)
![](images/annotated/detail/detail_view.png)

### Deleting an Expense

![](images/annotated/delete/delete.png)
![](images/annotated/delete/delete_success.png)

### Deleting all expenses in a month

In case you want to delete all the expenses in a month, you can do that too.

![](images/annotated/delete/delete_all.png)
![](images/annotated/delete/delete_all_modal.png)
![](images/annotated/delete/delete_all_success.png)

### Updating an Expense

![](images/annotated/update/update.png)
![](images/annotated/update/update_form.png)
![](images/annotated/update/update_succsess.png)

### Ordering of Expense Items
Expense item cards are ordered by "recent". The most recently added card shows up at front.

![](images/annotated/ordering/order.png)

### Expenses in the past month

![](images/annotated/past_month/past.png)
![](images/annotated/past_month/past_items.png)



### Visualizing monthly expenses
We can also visualize the expenses in form of a nice line chart

![](images/annotated/chart/chart.png)
![](images/annotated/chart/chart_view.png)

### Expense Badges
There are badges to indicate how much you spent compared to the last month

![](images/badges/spent_same.png)
![](images/badges/spent_more.png)
![](images/badges/spent_less.png)



### Pagination
If you have added enough items you will see the pagination links at the bottom to help you navigate across the pages

| First Page | Second Page | Third Page |
:-------------------------:|:-------------------------:|:-------------------------:
![](images/pagination/pagination_1.png)  |  ![](images/pagination/pagination_2.png) | ![](images/pagination/pagination_3.png)



![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)
![](images/base.png)

## Testing

```python
python manage.py test expenses
```
## 