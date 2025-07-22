# apps/loans/tasks.py

from celery import shared_task
import pandas as pd
from .models import Loan, Customer

@shared_task
def ingest_loan_data_task():
    try:
        df = pd.read_excel('data/loan_data.xlsx')
        
        loans_to_create = []
        customers_to_update = {}

        for _, row in df.iterrows():
            # Check if the customer for the loan exists in the database
            customer_exists = Customer.objects.filter(customer_id=row['Customer ID']).exists()
            if customer_exists:
                loans_to_create.append(
                    Loan(
                        customer_id=row['Customer ID'],
                        loan_id=row['Loan ID'],
                        loan_amount=row['Loan Amount'],
                        tenure=row['Tenure'],
                        interest_rate=row['Interest Rate'],
                        monthly_payment=row['Monthly payment'], 
                        emis_paid_on_time=row['EMIs paid on Time'], 
                        start_date=row['Date of Approval'], 
                        end_date=row['End Date'], 
                    )
                )
                
        
                cust_id = row['Customer ID']
                if cust_id not in customers_to_update:
                    customers_to_update[cust_id] = 0
                customers_to_update[cust_id] += row['Loan Amount']

        Loan.objects.bulk_create(loans_to_create, ignore_conflicts=True)
        
        for cust_id, total_loan in customers_to_update.items():
            Customer.objects.filter(pk=cust_id).update(current_debt=total_loan)

        return f"{len(loans_to_create)} loan records ingested successfully."
    except Exception as e:
        return f"Error ingesting loan data: {type(e).__name__} - {e}"