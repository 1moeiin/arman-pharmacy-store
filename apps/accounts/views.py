from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from .forms import AddressForm, PhoneAuthenticationForm, ProfileForm, RegisterForm
from .models import Address


class PhoneLoginView(LoginView):
    form_class = PhoneAuthenticationForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True
    extra_context = {"meta_title": "ورود به حساب کاربری"}


class PhoneLogoutView(LogoutView):
    next_page = reverse_lazy("core:home")


@ratelimit(key="ip", rate="5/h", method="POST", block=True)
def register(request):
    if request.user.is_authenticated:
        return redirect("core:home")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "ثبت‌نام با موفقیت انجام شد.")
            return redirect("core:home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form, "meta_title": "ثبت‌نام"})


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "اطلاعات با موفقیت به‌روزرسانی شد.")
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=request.user)
    addresses = request.user.addresses.all()
    return render(request, "accounts/profile.html", {
        "form": form,
        "addresses": addresses,
        "meta_title": "حساب کاربری من",
        "noindex": True,
    })


@login_required
def address_create(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "آدرس جدید اضافه شد.")
            return redirect("accounts:profile")
    else:
        form = AddressForm()
    return render(request, "accounts/address_form.html", {"form": form, "meta_title": "افزودن آدرس", "noindex": True})


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "آدرس به‌روزرسانی شد.")
            return redirect("accounts:profile")
    else:
        form = AddressForm(instance=address)
    return render(request, "accounts/address_form.html", {"form": form, "meta_title": "ویرایش آدرس", "noindex": True})


@login_required
@require_POST
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "آدرس حذف شد.")
    return redirect("accounts:profile")
