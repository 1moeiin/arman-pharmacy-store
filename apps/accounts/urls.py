from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.PhoneLoginView.as_view(), name="login"),
    path("logout/", views.PhoneLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile"),
    path("addresses/add/", views.address_create, name="address_create"),
    path("addresses/<int:pk>/edit/", views.address_edit, name="address_edit"),
    path("addresses/<int:pk>/delete/", views.address_delete, name="address_delete"),
]
