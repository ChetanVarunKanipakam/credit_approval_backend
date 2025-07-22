
from datetime import date
from django.db.models import Sum
from decimal import Decimal 
from dateutil.relativedelta import relativedelta

from .models import Loan, Customer


def calculate_credit_score(customer: Customer):
    # i. Past Loans paid on time
    all_loans = Loan.objects.filter(customer=customer)
    total_emis_paid = all_loans.aggregate(Sum('emis_paid_on_time'))['emis_paid_on_time__sum'] or 0
    total_tenure = all_loans.aggregate(Sum('tenure'))['tenure__sum'] or 0
    
    if total_tenure > 0:
        on_time_payment_ratio = total_emis_paid / total_tenure
        credit_score_a = on_time_payment_ratio * 30  # Weight: 30
    else:
        credit_score_a = 30 # No past loans, good start

    # ii. No of loans taken in past
    num_loans = all_loans.count()
    credit_score_b = max(0, 20 - num_loans * 4) # Weight: 20

    # iii. Loan activity in current year
    current_year_loans = all_loans.filter(start_date__year=date.today().year).count()
    credit_score_c = max(0, 20 - current_year_loans * 5) # Weight: 20

    # iv. Loan approved volume
    total_loan_volume = all_loans.aggregate(Sum('loan_amount'))['loan_amount__sum'] or 0
    if total_loan_volume > customer.approved_limit * 2: # High volume might be risky
        credit_score_d = 0
    else:
        credit_score_d = 30 # Weight: 30

    # v. Sum of current loans > approved limit
    current_loans_amount = customer.current_debt
    if current_loans_amount > customer.approved_limit:
        return 0

    credit_score = int(credit_score_a + credit_score_b + credit_score_c + credit_score_d)
    return min(100, credit_score)


def calculate_emi(principal, annual_rate, tenure_months):
    # Ensure all inputs are Decimals for precision
    principal = Decimal(principal)
    annual_rate = Decimal(annual_rate)
    
    if annual_rate == 0:
        return round(principal / Decimal(tenure_months), 2)
        
    # Perform all calculations with Decimal
    monthly_rate = annual_rate / Decimal('12') / Decimal('100')
    n = Decimal(tenure_months)
    
    # EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
    one_plus_r = 1 + monthly_rate
    emi = (principal * monthly_rate * (one_plus_r**n)) / (one_plus_r**n - 1)
    
    # Round to 2 decimal places
    return round(emi, 2)


def check_loan_eligibility(customer: Customer, requested_interest_rate, loan_amount, tenure):
    credit_score = calculate_credit_score(customer)
    
    current_emis = Loan.objects.filter(customer=customer, end_date__gte=date.today()).aggregate(Sum('monthly_payment'))['monthly_payment__sum'] or 0
    
    # We still need to calculate the potential new EMI for the check
    potential_new_emi = calculate_emi(loan_amount, requested_interest_rate, tenure)
    
    # CHECK 1: Total EMI must be <= 50% of monthly salary
    if (current_emis + potential_new_emi) > (customer.monthly_salary * 0.5):
        # Return a full-shaped dictionary, even on failure
        return {
            "customer_id": customer.customer_id,
            "approval": False,
            "interest_rate": requested_interest_rate,
            "corrected_interest_rate": None,
            "tenure": tenure,
            "monthly_installment": potential_new_emi, # Show what the installment would have been
            "message": "Total EMI exceeds 50% of monthly salary." 
        }

    # CHECK 2: Based on credit score
    approval = False
    corrected_interest_rate = requested_interest_rate

    if credit_score > 50:
        approval = True
    elif 50 >= credit_score > 30:
        if requested_interest_rate > 12:
            approval = True
        else:
            corrected_interest_rate = Decimal('12.00')
            approval = True
    elif 30 >= credit_score > 10:
        if requested_interest_rate > 16:
            approval = True
        else:
            corrected_interest_rate = Decimal('16.00')
            approval = True
    else: # score <= 10
        approval = False
        
    final_interest_rate = corrected_interest_rate if corrected_interest_rate != requested_interest_rate else requested_interest_rate
    
    # If not approved by credit score, return a full-shaped dictionary
    if not approval:
        return {
            "customer_id": customer.customer_id,
            "approval": False,
            "interest_rate": requested_interest_rate,
            "corrected_interest_rate": None,
            "tenure": tenure,
            "monthly_installment": potential_new_emi,
            "message": "Loan not approved based on credit score."
        }

    # If all checks pass, calculate final monthly installment and return
    monthly_installment = calculate_emi(loan_amount, final_interest_rate, tenure)

    return {
        "customer_id": customer.customer_id,
        "approval": approval,
        "interest_rate": requested_interest_rate,
        "corrected_interest_rate": corrected_interest_rate if corrected_interest_rate != requested_interest_rate else None,
        "tenure": tenure,
        "monthly_installment": monthly_installment,
        "message": "Loan approved." 
    }