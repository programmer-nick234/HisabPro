from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, login_view, logout_view, user_view,
    update_profile_view, change_password_view
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('user/', user_view, name='user'),
    path('profile/', update_profile_view, name='update_profile'),
    path('change-password/', change_password_view, name='change_password'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
