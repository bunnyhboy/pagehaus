# from django.contrib.auth import authenticate
# from rest_framework import serializers,status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.http import urlsafe_base64_encode
# from django.utils.encoding import force_bytes
# from django.core.mail import send_mail
# from django.conf import settings
# from django.utils.encoding import force_bytes, force_str
# from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode



# from .models import User


# class RegisterSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ["id", "username", "email", "password"]
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         user.is_email_verified=False
#         user.save(update_fields=["is_email_verified"])

#         uid = urlsafe_base64_encode(force_bytes(user.pk))
#         token = default_token_generator.make_token(user)

#         verification_url = (
#             f"http://127.0.0.1:8000/auth/"
#             f"verify-email/{uid}/{token}/"
#         )

#         send_mail(
#             subject="Verify your email",
#             message=(
#                 f"Hello {user.username},\n\n"
#                 f"Click the link below to verify your email:\n\n"
#                 f"{verification_url}\n\n"
#                 f"If you did not create this account, ignore this email."
#             ),
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#         )
#         return user


# class LoginSerializer(serializers.Serializer):

#     username = serializers.CharField()
#     password = serializers.CharField(write_only=True)

#     def validate(self, data):

#         user = authenticate(
#             username=data["username"],
#             password=data["password"]
#         )

#         if not user:
#             raise serializers.ValidationError("Invalid credentials")

#         if not user.is_email_verified:
#             raise serializers.ValidationError(
#                 {"detail": "Please verify your email before logging in."}
#             )

#         refresh = RefreshToken.for_user(user)

#         return {
#             "user": user,
#             "access": str(refresh.access_token),
#             "refresh": str(refresh)
#         }


# class UserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ["id", "username", "email"]



from django.contrib.auth import authenticate
from rest_framework import serializers,status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .utils import send_verification_email


from .models import User,UserProfile


class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "username": {"validators": []},
            "email": {"validators": []},
        }

    def validate(self, data):
        username = data["username"]
        email = data["email"]

        username_user = User.objects.filter(
            username=username
        ).first()

        email_user = User.objects.filter(
            email=email
        ).first()

        if username_user:
            if username_user.is_email_verified:
                raise serializers.ValidationError({
                    "username": "A user with that username already exists."
                })

        if email_user:
            if email_user.is_email_verified:
                raise serializers.ValidationError({
                    "email": "A user with that email already exists."
                })

        if username_user or email_user:

            existing_user = username_user or email_user

            if username_user and email_user:
                if username_user.pk != email_user.pk:
                    raise serializers.ValidationError({
                        "detail": (
                            "The username and email belong to "
                            "different accounts."
                        )
                    })

            data["existing_user"] = existing_user

        return data

    def create(self, validated_data):

        existing_user = validated_data.pop("existing_user", None)

        if existing_user:

            send_verification_email(existing_user)

            return existing_user

        user = User.objects.create_user(**validated_data)

        user.is_email_verified = False
        user.save(update_fields=["is_email_verified"])

        send_verification_email(user)

        return user


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):

        user = authenticate(
            username=data["username"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        if not user.is_email_verified:
            raise serializers.ValidationError(
                {"detail": "Please verify your email before logging in."}
            )

        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = [
            "avatar",
            "phone",
            "bio",
            "location",
        ]
