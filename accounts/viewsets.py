from django.http import Http404
from emails.utils.emails import BaseEmail
from rest_framework import generics
from rest_framework import status

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,permission_classes,authentication_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User, update_last_login
from .serializers import *

import logging
from accounts.otp_generate import generate_otp
logger = logging.getLogger(__name__)

class LoginView(APIView):
    """
    employee login and get token
    """
    # authentication_classes = [authentication.a]
    permission_classes = [permissions.AllowAny]
    serializer_class = AuthTokenSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data,context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        update_last_login(None, token.user)
        response = {
            'token': token.key,
            'roles': list(user.roles.all().values_list('id', flat=True))
        }
        return Response(response)
    
    
class LogoutView(APIView):
    """
    Agents logout
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, format=None):
        user = self.request.user
        tokens = Token.objects.filter(user=user)
        if tokens:
            tokens.delete()
        return Response({'message': "successfully logout"})
    
    
class ProfileAPIView(generics.RetrieveUpdateAPIView):
    """
    GET and UPDATE user profile
    """
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    
    def get_queryset(self):
        queryset = Profile.objects.filter(user=self.request.user)
        return queryset
    
    def get_object(self):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            return queryset.get(user=self.request.user)
        except Profile.DoesNotExist:
            logger.info("user profile doesnot found so creating it")
            profile, is_created = Profile.objects.get_or_create(user=self.request.user)
            return profile
        
    def update(self, request, *args, **kwargs):
        user_profile = self.get_object()
        serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
            

@api_view(['POST'])
@permission_classes([permissions.AllowAny])   
def frogot_password(request):
    """
    Request a OTP through mail to set new password
    """
    forgot_password_serializer = ForgotPasswordSerializer(data=request.POST)
    forgot_password_serializer.is_valid(raise_exception=True)
    email = forgot_password_serializer.data['email']
    
    try:
        otp = generate_otp()
        EmailOtp.objects.filter(email=email).delete()
        EmailOtp.objects.create(name="forgot password", otp=otp, email=email)
        email_subject = "leave management Alert"
        mailcontent = """Hi, OTP to change the password is {} """.format(otp)
        recipient_list = [email]
        mail_dict = {
            'subject': email_subject,
            'plain_message': mailcontent,
            'recipient_list': recipient_list, 
        }
        BaseEmail.send_mail(**mail_dict)
    except Exception as e:
        logger.info("unable to send otp {}".format(e))
    return Response({"message":"OTP sent to email"})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])  
def verify_otp(request):
    """
    Verify email otp and if success send auth token to client
    """
    email_otp_serializer = EmailOtpSerializer(data=request.data)
    email_otp_serializer.is_valid(raise_exception=True)
    email = email_otp_serializer.data['email']
    user = User.objects.get(email=email)
    token, created = Token.objects.get_or_create(user=user)
    return Response({'token': token.key})
    
    
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])    
def change_password(request):
    """
    change password new_password1 and new_password2 and return token to client
    """
    change_password_serializer = ChangePasswordSerializer(data=request.POST, context={'request': request})
    change_password_serializer.is_valid(raise_exception=True)
    change_password_serializer.save()
    return Response({'message': 'Your new password was set successfully'})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@authentication_classes([authentication.TokenAuthentication])
def change_old_password(request):
    """
    set new password using old password
    """
    change_password_serializer = ChangeOldPasswordSerializer(data=request.POST, context={'request': request})
    change_password_serializer.is_valid(raise_exception=True)
    change_password_serializer.save()
    return Response({'message': 'Your new password was set successfully'})
