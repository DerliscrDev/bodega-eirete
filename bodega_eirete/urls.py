# bodega_eirete/urls.py
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('', include('bodega.urls')),
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),
    path("login/", LoginView.as_view(
        template_name="registration/login.html",
        redirect_authenticated_user=True
    ), name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]

