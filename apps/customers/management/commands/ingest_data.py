from django.core.management.base import BaseCommand
from apps.customers.tasks import ingest_customer_data_task
from apps.loans.tasks import ingest_loan_data_task

class Command(BaseCommand):
    help = 'Ingests customer and loan data from Excel files into the database via background workers.'

    def handle(self, *args, **options):
        self.stdout.write('Queuing customer data ingestion task...')
        ingest_customer_data_task.delay()
        self.stdout.write(self.style.SUCCESS('Customer data ingestion task queued.'))
        
        self.stdout.write('Queuing loan data ingestion task...')
        ingest_loan_data_task.delay()
        self.stdout.write(self.style.SUCCESS('Loan data ingestion task queued.'))