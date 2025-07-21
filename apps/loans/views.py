from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from dateutil.relativedelta import relativedelta
from datetime import date

from apps.customers.models import Customer
from .models import Loan
from . import services
from .serializers import (
    EligibilityRequestSerializer, EligibilityResponseSerializer,
    CreateLoanRequestSerializer, CreateLoanResponseSerializer,
    ViewLoanSerializer, ViewCustomerLoanSerializer
)


class CheckEligibilityView(APIView):
    def post(self, request):
        serializer = EligibilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer = get_object_or_404(Customer, pk=data['customer_id'])
        
        eligibility_data = services.check_loan_eligibility(
            customer, data['interest_rate'], data['loan_amount'], data['tenure']
        )
        
        response_serializer = EligibilityResponseSerializer(eligibility_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class CreateLoanView(APIView):
    def post(self, request):
        serializer = CreateLoanRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        customer = get_object_or_404(Customer, pk=data['customer_id'])
        
        eligibility_data = services.check_loan_eligibility(
            customer, data['interest_rate'], data['loan_amount'], data['tenure']
        )

        if not eligibility_data['approval']:
            response_data = {
                "loan_id": None,
                "customer_id": customer.customer_id,
                "loan_approved": False,
                "message": eligibility_data.get("message", "Loan not approved."),
                "monthly_installment": None
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        # If approved, create the loan
        final_interest_rate = eligibility_data['corrected_interest_rate'] if eligibility_data['corrected_interest_rate'] else data['interest_rate']
        
        new_loan = Loan.objects.create(
            customer=customer,
            loan_amount=data['loan_amount'],
            tenure=data['tenure'],
            interest_rate=final_interest_rate,
            monthly_payment=eligibility_data['monthly_installment'],
            emis_paid_on_time=0,
            start_date=date.today(),
            end_date=date.today() + relativedelta(months=data['tenure'])
        )
        
        # Update customer's current debt
        customer.current_debt += data['loan_amount']
        customer.save()

        response_data = {
            "loan_id": new_loan.loan_id,
            "customer_id": customer.customer_id,
            "loan_approved": True,
            "message": "Loan approved and created successfully.",
            "monthly_installment": new_loan.monthly_payment
        }
        response_serializer = CreateLoanResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ViewLoanView(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, pk=loan_id)
        serializer = ViewLoanSerializer(loan)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ViewCustomerLoansView(APIView):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, pk=customer_id)
        loans = Loan.objects.filter(customer=customer)
        serializer = ViewCustomerLoanSerializer(loans, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)