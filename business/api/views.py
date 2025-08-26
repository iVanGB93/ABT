from django.core.mail.message import EmailMessage
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth.models import User

from .serializers import BusinessSerializer, ExtraIncomeSerializer, ExtraExpenseSerializer, PaymentMethodTypeSerializer, PaymentMethodSerializer
from business.models import Business, ExtraIncome, ExtraExpense, Invitation, PaymentMethodType
import threading
import json

class EmailSending(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=True)

class BusinessesView(APIView):

    def get(self, request, queryset=None, **kwargs):
        owner = self.kwargs.get('pk')
        if User.objects.filter(username=owner).exists():
            owner_user = User.objects.get(username=owner)
            businesses = Business.objects.filter(owners=owner_user)
            data = []
            for business in businesses:
                data.append(BusinessSerializer(business).data)
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            data = {'message': 'Owner does not exist.'}
            return Response(status=status.HTTP_404_NOT_FOUND, data=data)
    
class BusinessView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        owner_id = self.kwargs.get('pk') 
        business = Business.objects.get(id=owner_id)
        data = BusinessSerializer(business).data
        return Response(status=status.HTTP_200_OK, data=data)

    def post(self, request, queryset=None, **kwargs):
        pk = self.kwargs.get('pk')
        data = request.data
        action = data['action']
        response = {'OK': False}
        if action == 'delete':
            if Business.objects.filter(id=pk).exists():
                business = Business.objects.get(id=pk)
                business.delete()
                response['message'] = "Business Deleted."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Business not found."
                return Response(status=status.HTTP_200_OK, data=response)
        owner = User.objects.get(username=pk)
        if action == 'new':
            name = data['name']
            if Business.objects.filter(name=name).exists():
                response['message'] = "Business with this name already exists."
                return Response(status=status.HTTP_200_OK, data=response)
            description = data.get('description', 'no description saved')
            phone = data.get('phone', 'no phone saved')
            email = data.get('email', 'no email saved')
            address = data.get('address', 'no address saved')
            address2 = data.get('address2', 'no extra address saved')
            new_business = Business(name=name, description=description, phone=phone, email=email, address=address, address2=address2)
            new_business.logo = data.get('image', new_business.logo)
            if data.get('owners'):
                owners = data['owners']
                if isinstance(owners, list):
                    owner_emails = User.objects.filter(email__in=owners)
                    for owner_email in owner_emails:
                        invitation = Invitation.objects.create(
                            business=new_business,
                            inviter=owner,
                            email=owner_email,
                        )
                        invitation.save()
                        email = EmailMessage('ABT - Ownership invitation', f'{owner.username} invited you to be owner of {new_business.name}. Go to "https://abt.qbared.com/business/invitation/{invitation.code}/" to accept. Use the code: {invitation.code}', None, [owner_email])
                        EmailSending(email).start()
                else:
                    for no_user in owners:
                        email = EmailMessage('ABT - Ownership invitation', f'{owner.username} invited you to be owner of {new_business.name}, you are not registered yet. Please register at "https://abt.qbared.com/user/register/', None, [no_user])
                        EmailSending(email).start()
            new_business.save()
            new_business.owners.set([owner])
            business_data = BusinessSerializer(new_business).data
            response['business'] = business_data
            response['message'] = "New business created."
            response['OK'] = True
        if action == 'update':
            if not data.get('id'):
                response['message'] = "Business id required."
                return Response(status=status.HTTP_200_OK, data=response)
            if Business.objects.filter(id=data['id']).exists():
                business = Business.objects.get(id=data['id'])
                business.name = data.get('name', business.name)
                business.description = data.get('description', business.description)
                business.email = data.get('email', business.email)
                business.phone = data.get('phone', business.phone)
                business.address = data.get('address', business.address)
                business.address2 = data.get('address2', business.address2)
                business.logo = data.get('image', business.logo)
                owners = data.get('owners', [])
                if isinstance(owners, str):
                    try:
                        owners = json.loads(owners)
                        if len(owners) > 0:
                            registered_emails = []
                            not_registered_emails = []
                            for owner in owners:
                                if User.objects.filter(email=owner).exists():
                                    registered_emails.append(owner)
                                else:
                                    not_registered_emails.append(owner)
                            for owner_email in registered_emails:
                                inviter = User.objects.get(email=owner_email)
                                invitation = Invitation.objects.create(
                                    business=business,
                                    inviter=inviter,
                                    email=owner_email,
                                )
                                invitation.save()
                                email = EmailMessage('ABT - Ownership invitation', f'{inviter.username} invited you to be owner of {business.name}. Go to "https://abt.qbared.com/business/invitation/{invitation.code}/" to accept. Use the code: {invitation.code}', None, [owner_email])
                                EmailSending(email).start()
                            for owner_email in not_registered_emails:
                                inviter = User.objects.get(email=owner_email)
                                invitation = Invitation.objects.create(
                                    business=business,
                                    inviter=inviter,
                                    email=owner_email,
                                )
                                invitation.save()
                                email = EmailMessage('ABT - Ownership invitation', f'{inviter.username} invited you to be owner of {business.name}, you are not registered yet. Please register at "https://abt.qbared.com/user/register/', None, [owner_email])
                                EmailSending(email).start()
                        else:
                            print('No owners provided')
                    except json.JSONDecodeError:
                        owners = [owners]
                business.save()
                business_data = BusinessSerializer(business).data
                response['message'] = "Business Updated."
                response['business'] = business_data
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "Business not found."
                return Response(status=status.HTTP_200_OK, data=response)
        return Response(status=status.HTTP_200_OK, data=response)  

class ExtrasView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        business_name = self.kwargs.get('pk')
        if Business.objects.filter(name=business_name).exists():
            business = Business.objects.get(name=business_name)
            extra_income = business.extra_income.all()
            extra_expenses = business.extra_expenses.all()
            data = {
                'extra_income': [ExtraIncomeSerializer(income).data for income in extra_income],
                'extra_expenses': [ExtraExpenseSerializer(expense).data for expense in extra_expenses]
            }
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Business not found.'})

    def post(self, request, queryset=None, **kwargs):
        data = request.data
        action = data['action']
        type = data['type']
        response = {'OK': False}
        if action == 'delete':
            id = data.get('id')
            if type == 'income':
                if id and ExtraIncome.objects.filter(id=id).exists():
                    ExtraIncome.objects.get(id=id).delete()
                    response['message'] = "Extra income deleted."
                    response['OK'] = True
                    return Response(status=status.HTTP_200_OK, data=response)
                else:
                    response['message'] = "Extra income not found."
                    return Response(status=status.HTTP_404_NOT_FOUND, data=response)
            elif type == 'expense':
                if id and ExtraExpense.objects.filter(id=id).exists():
                    ExtraExpense.objects.get(id=id).delete()
                    response['message'] = "Extra expense deleted."
                    response['OK'] = True
                    return Response(status=status.HTTP_200_OK, data=response)
                else:
                    response['message'] = "Extra expense not found."
                    return Response(status=status.HTTP_404_NOT_FOUND, data=response)
        business_name = self.kwargs.get('pk')
        business = Business.objects.get(name=business_name)
        if action == 'new':
            if type == 'income':
                new_income = ExtraIncome(business=business, amount=data.get('amount', 0), description=data.get('description', ''))
                new_income.image = data.get('image', new_income.image)
                new_income.save()
                response['message'] = "Extra income created."
                response['OK'] = True
                return Response(status=status.HTTP_201_CREATED, data=response)
            elif type == 'expense':
                deductible = data.get('deductible', 'true')
                if deductible == 'false':
                    deductible = False
                else:
                    deductible = True
                new_expense = ExtraExpense(business=business, amount=data.get('amount', 0), description=data.get('description', ''), category=data.get('category', 'other'), tax_deductible=deductible)
                new_expense.image = data.get('image', new_expense.image)
                new_expense.save()
                response['message'] = "Extra expense created."
                response['OK'] = True
                return Response(status=status.HTTP_201_CREATED, data=response)
            else:
                response['message'] = "Invalid action."
                return Response(status=status.HTTP_400_BAD_REQUEST, data=response)
        if action == 'update':
            if type == 'income':
                id = data.get('id')
                if id and ExtraIncome.objects.filter(id=id).exists():
                    extra_income = ExtraIncome.objects.get(id=id)
                    extra_income.amount = data.get('amount', extra_income.amount)
                    extra_income.description = data.get('description', extra_income.description)
                    extra_income.image = data.get('image', extra_income.image)
                    extra_income.save()
                    response['message'] = "Extra income updated."
                    response['OK'] = True
                    return Response(status=status.HTTP_200_OK, data=response)
                else:
                    response['message'] = "Extra income not found."
                    return Response(status=status.HTTP_404_NOT_FOUND, data=response)
            elif type == 'expense':
                id = data.get('id')
                if id and ExtraExpense.objects.filter(id=id).exists():
                    extra_expense = ExtraExpense.objects.get(id=id)
                    extra_expense.amount = data.get('amount', extra_expense.amount)
                    extra_expense.description = data.get('description', extra_expense.description)
                    extra_expense.image = data.get('image', extra_expense.image)
                    extra_expense.category = data.get('category', extra_expense.category)
                    deductible = data.get('deductible', 'true')
                    if deductible == 'false':
                        deductible = False
                    else:
                        deductible = True
                    extra_expense.tax_deductible = deductible
                    extra_expense.save()
                    response['message'] = "Extra expense updated."
                    response['OK'] = True
                    return Response(status=status.HTTP_200_OK, data=response)
                else:
                    response['message'] = "Extra expense not found."
                    return Response(status=status.HTTP_404_NOT_FOUND, data=response)
            
class OwnersView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        business_name = self.kwargs.get('pk')
        if Business.objects.filter(name=business_name).exists():
            business = Business.objects.get(name=business_name)
            owners = business.owners.all()
            data = [owner.username for owner in owners]
            return Response(status=status.HTTP_200_OK, data=data)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Business not found.'})
        
    def post(self, request, queryset=None, **kwargs):
        business_name = self.kwargs.get('pk')
        data = request.data
        action = data['action']
        response = {'OK': False}
        if not Business.objects.filter(name=business_name).exists():
            response['message'] = "Business not found."
            return Response(status=status.HTTP_404_NOT_FOUND, data=response)
        
        business = Business.objects.get(name=business_name)
        if action == 'add':
            username = data.get('username')
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                business.owners.add(user)
                response['message'] = "Owner added."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "User not found."
                return Response(status=status.HTTP_404_NOT_FOUND, data=response)
        
        elif action == 'remove':
            username = data.get('username')
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
                business.owners.remove(user)
                response['message'] = "Owner removed."
                response['OK'] = True
                return Response(status=status.HTTP_200_OK, data=response)
            else:
                response['message'] = "User not found."
                return Response(status=status.HTTP_404_NOT_FOUND, data=response)
    

class PaymentMethodTypeView(APIView):

    def get(self, request, *args, **kwargs):
        types = PaymentMethodType.objects.all()
        serializer = PaymentMethodTypeSerializer(types, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class PaymentMethodView(APIView):

    def get(self, request, *args, **kwargs):
        response = {'OK': False}
        business_id = self.kwargs.get('pk')
        if Business.objects.filter(id=business_id).exists():
            business = Business.objects.get(id=business_id)
            payment_methods = business.payment_methods.all()
            serializer = PaymentMethodSerializer(payment_methods, many=True)
            response['OK'] = True
            response['data'] = serializer.data
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        else:
            response['message'] = 'Business not found.'
            return Response(status=status.HTTP_404_NOT_FOUND, data=response)

    def post(self, request, *args, **kwargs):
        response = {'OK': False}
        business_id = self.kwargs.get('pk')
        if Business.objects.filter(id=business_id).exists():
            business = Business.objects.get(id=business_id)
            data = request.data
            payment_method_type_id = data.get('payment_type_id')
            payment_method_type = PaymentMethodType.objects.get(id=payment_method_type_id)
            data['business'] = business.pk
            data['payment_type'] = payment_method_type.pk
            serializer = PaymentMethodSerializer(data=data)
            if serializer.is_valid():
                payment_method = serializer.save(business=business)
                response['OK'] = True
                response['data'] = PaymentMethodSerializer(payment_method).data
                return Response(status=status.HTTP_201_CREATED, data=response)
            response['message'] = 'Invalid data.'
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, data=response)
        response['message'] = 'Business not found.'
        return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, data=response)

    def put(self, request, *args, **kwargs):
        business_id = self.kwargs.get('pk')
        if Business.objects.filter(id=business_id).exists():
            business = Business.objects.get(id=business_id)
            payment_method_id = request.data.get('id')
            if not payment_method_id:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Payment method ID is required.'})
            if business.payment_methods.filter(id=payment_method_id).exists():
                payment_method = business.payment_methods.get(id=payment_method_id)
                serializer = PaymentMethodSerializer(payment_method, data=request.data, partial=True)
                if serializer.is_valid():
                    updated_payment_method = serializer.save()
                    return Response(status=status.HTTP_200_OK, data=PaymentMethodSerializer(updated_payment_method).data)
                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Payment method not found for this business.'})
        return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Business not found.'})

    def delete(self, request, *args, **kwargs):
        business_id = self.kwargs.get('pk')
        if Business.objects.filter(id=business_id).exists():
            business = Business.objects.get(id=business_id)
            payment_method_id = self.kwargs.get('payment_method_id')
            if not payment_method_id:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={'message': 'Payment method ID is required.'})
            if business.payment_methods.filter(id=payment_method_id).exists():
                payment_method = business.payment_methods.get(id=payment_method_id)
                payment_method.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Payment method not found for this business.'})
        return Response(status=status.HTTP_404_NOT_FOUND, data={'message': 'Business not found.'})
