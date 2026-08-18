from django.urls import path
from .views import RegisterView,LoginView,LogoutView,MeView,VerifyEmailView,ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "verify-email/<uidb64>/<token>/",
        VerifyEmailView.as_view(),
        name="verify-email",
    ),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", MeView.as_view(), name="me"),
     path(
        "profile/",
        ProfileView.as_view(),
        name="profile"
    ),
]