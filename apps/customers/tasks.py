from celery import shared_task
import pandas as pd
from .models import Customer

@shared_task
def ingest_customer_data_task():
    try:
        df = pd.read_excel('data/customer_data.xlsx')
        customers_to_create = []
        for _, row in df.iterrows():
            customers_to_create.append(
                Customer(
    
                    customer_id=row['Customer ID'],
                    first_name=row['First Name'],
                    last_name=row['Last Name'],
                    phone_number=row['Phone Number'],
                    monthly_salary=row['Monthly Salary'],
                    approved_limit=row['Approved Limit'],
                    current_debt=0 
                )
            )
        
        Customer.objects.bulk_create(customers_to_create, ignore_conflicts=True)
        return f"{len(customers_to_create)} customer records ingested successfully."
    except Exception as e:
        return f"Error ingesting customer data: {type(e).__name__} - {e}"