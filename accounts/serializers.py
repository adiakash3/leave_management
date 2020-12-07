from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation

from rest_framework import serializers

from .models import *
from django.utils.translation import ugettext_lazy as _

User = get_user_model()

class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(trim_whitespace=True)
    password = serializers.CharField(trim_whitespace=True)

    def validate(self, attrs):
        username = attrs.get('email')
        password = attrs.get('password')

        if username and password:
            if User.objects.filter(email__iexact=username).exists():
                user = User.objects.get(email__iexact=username)
                if not user.roles.filter(id__in=[Role.EMPLOYEE, Role.MANAGER, Role.TEAM_LEADER]).exists():
                    msg = _('Only employee can login.')
                    raise serializers.ValidationError(msg, code='authorization')
            user = authenticate(request=self.context.get('request'),
                                email=username, password=password)

            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
    
    
class ProfileSerializer(serializers.ModelSerializer):
    """
    profile update and user stuff
    """
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    mobile_number = serializers.CharField(source="user.mobile_number")
    roles = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    
    class Meta:
        model = Profile
        fields = ["image", "first_name", "last_name", "email", "mobile_number", "city", "age", "gender", 'roles', 'code']
        
    def update(self, instance, validated_data):
        instance.city = validated_data.get('city', instance.city)
        instance.age = validated_data.get('age', instance.age)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.image = validated_data.get('image', instance.image)
        if validated_data.get('user'):
            instance.user.first_name = validated_data['user'].get('first_name', instance.user.first_name)
            instance.user.last_name = validated_data['user'].get('last_name', instance.user.last_name)
            instance.user.email = validated_data['user'].get('email', instance.user.email)
            instance.user.mobile_number = validated_data['user'].get('mobile_number', instance.user.mobile_number)
            instance.user.save()
        instance.save()
        return instance
    
    def get_gender(self,obj):
        return obj.get_gender_display()
    
    def get_roles(self, obj):
        return obj.user.roles.all().values_list('id', flat=True)
    
    def get_code(self, obj):
        try:
            return obj.user.employee.code
        except Exception as e:
            return "ID not assigned"
        

    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(trim_whitespace=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        
        if not User.objects.filter(email__iexact=email).exists():
            msg = _("given email doest not exists")
            raise serializers.ValidationError(msg)
        return attrs
    
    
class EmailOtpSerializer(serializers.Serializer):
    otp = serializers.CharField(trim_whitespace=True)
    email = serializers.EmailField(trim_whitespace=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        if not EmailOtp.objects.filter(email__iexact=email, otp__iexact=otp).exists():
            msg = _("Please enter valid otp")
            raise serializers.ValidationError(msg)
        EmailOtp.objects.filter(email__iexact=email, otp__iexact=otp).delete()
        return attrs
    
    
class ChangePasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        password_validation.validate_password(data['new_password1'])
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user


class ChangeOldPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password1 = serializers.CharField(max_length=128, write_only=True, required=True)
    new_password2 = serializers.CharField(max_length=128, write_only=True, required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                _('Your old password was entered incorrectly. Please enter it again.')
            )
        return value

    def validate(self, data):
        if data.get('old_password') == data.get('new_password1'):
            raise serializers.ValidationError({'old_password': "New password is same as old password!"})
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError({'new_password2': _("The two password fields didn't match.")})
        password_validation.validate_password(data['new_password1'])
        return data

    def save(self, **kwargs):
        password = self.validated_data['new_password1']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user
