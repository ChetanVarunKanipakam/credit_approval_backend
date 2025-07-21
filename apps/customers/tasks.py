# apps/customers/tasks.py

from celery import shared_task
import pandas as pd
from .models import Customer

@shared_task
def ingest_customer_data_task():
    try:
        # Load the Excel file
        df = pd.read_excel('data/customer_data.xlsx')
        
        # Prepare a list of Customer objects to be created
        customers_to_create = []
        for _, row in df.iterrows():
            customers_to_create.append(
                Customer(
                    # Use the EXACT column names from the Excel file
                    customer_id=row['Customer ID'],
                    first_name=row['First Name'],
                    last_name=row['Last Name'],
                    phone_number=row['Phone Number'],
                    monthly_salary=row['Monthly Salary'],
                    approved_limit=row['Approved Limit'],
                    current_debt=0 # Assuming new customers from this sheet have 0 debt
                )
            )
        
        # Use bulk_create for efficiency, ignoring conflicts if a customer_id already exists
        Customer.objects.bulk_create(customers_to_create, ignore_conflicts=True)
        return f"{len(customers_to_create)} customer records ingested successfully."
    except Exception as e:
        # Return a more descriptive error message
        return f"Error ingesting customer data: {type(e).__name__} - {e}"