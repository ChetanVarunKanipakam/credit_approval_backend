import math
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer
from .serializers import RegisterCustomerSerializer, CustomerResponseSerializer

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            validated_data = serializer.validated_data
            monthly_salary = validated_data['monthly_salary']

            # Calculate approved limit
            approved_limit = round(36 * monthly_salary / 100000) * 100000

            customer = Customer.objects.create(
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                age=validated_data['age'],
                phone_number=validated_data['phone_number'],
                monthly_salary=monthly_salary,
                approved_limit=approved_limit,
                current_debt=0  
            )

            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)