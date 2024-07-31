from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from .serializers import AccountSerializer
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone

from user.models import RegistrationCode
from django.core.mail.message import EmailMessage
import threading

from user.models import Profile

class EmailSending(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    
    def run(self):
        self.email.send(fail_silently=False)

class RegisterView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, queryset=None, **kwargs):
        data = request.data
        response = {'OK': False}
        action = data['action']
        email = data['email']
        if action == 'email':
            if User.objects.filter(email=email).exists():
                response['message'] = "This email is already taken."
                return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, data=response)
            else:
                if RegistrationCode.objects.filter(email=email).exists():
                    new_code = RegistrationCode.objects.get(email=email)
                else:
                    new_code = RegistrationCode(email=email)
                    new_code.save()
                email = EmailMessage('Welcome to ABT', f'Here is your code for continuing registering {new_code.code}', None, [email])
                EmailSending(email).start()
                response['message'] = "A code was send to your email, please check it and continue."
                response['code'] = new_code.code
                response['email'] = new_code.email
                return Response(status=status.HTTP_200_OK, data=response)
        username = data['username']
        password = data['password']
        if User.objects.filter(username=username).exists():
            response['message'] = "Username is already taken."
            return Response(status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION, data=response)
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        new_user.save()
        code = RegistrationCode.objects.get(email=email)
        code.user = new_user
        code.dateEnd = timezone.now()
        code.save()
        response['message'] = "Account created."
        return Response(status=status.HTTP_201_CREATED, data=response)

class AccountView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, queryset=None, **kwargs):
        user = self.kwargs.get('pk')
        user = User.objects.get(username=user)
        profile = Profile.objects.get(user=user)
        data = AccountSerializer(profile).data
        return Response(status=status.HTTP_200_OK, data=data)
    
    def post(self, request, queryset=None, **kwargs):
        data = request.data
        user = self.kwargs.get('pk')
        user = User.objects.get(username=user)
        profile = Profile.objects.get(user=user)
        profile.business_name = data.get('business_name', profile.business_name)
        profile.business_logo = data.get('business_logo', profile.business_logo)
        profile.phone = data.get('phone', profile.phone)
        profile.address = data.get('address', profile.address)
        user.email = data.get('email', user.email)
        user.save()
        profile.save()
        data = AccountSerializer(profile).data
        return Response(status=status.HTTP_200_OK, data=data)

