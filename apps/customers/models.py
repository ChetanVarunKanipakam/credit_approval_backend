from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.customer_id})'