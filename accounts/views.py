# Django se zaroori modules import karein
from django.shortcuts import render, redirect,HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
import uuid

# View functions define karein
# login_required decorator se ensure karein ki sirf login users hi home page tak pahunch saken
@login_required(login_url="/")
def home(request):   
    return render(request, 'home.html')

# login_attempt view define karein
def login_attempt(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.success(request, "User not found")
            return redirect('/login')
        profile_obj = Profile.objects.filter(user=user_obj).first()
        if not profile_obj.is_verified:
            messages.success(request, "Profile is not verified, check your mail.")
            return redirect('/login')
        # if authenticate(username=username, password=password):
        #     messages.success(request, "Wrong password")
        #     return redirect('/login')
        user = authenticate(username=username, password=password)
        if user is None:
            messages.success(request, "Wrong password")
            return redirect('/login')
        login(request, user)
        return redirect('/')
    return render(request, 'login.html')

# register_attempt view define karein
def register_attempt(request):
    if request.method == 'POST':
        # Form se username, email, aur password extract karein
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Agar username already taken hai to message show karein aur register page pe redirect karein
            if User.objects.filter(username=username).first():
                messages.success(request, "Username is taken")
                return redirect('/register')

            # User object create karein, password set karein, aur save karein
            user_obj = User(username=username, email=email)
            user_obj.set_password(password)
            user_obj.save()

            # Auth token generate karein, profile create karein, aur save karein
            auth_token = str(uuid.uuid4())
            profile_obj = Profile.objects.create(user=user_obj, auth_token=auth_token)
            profile_obj.save()

            # Email send karein
            send_mail_after_registration(email, auth_token)

            # Token page pe redirect karein
            return redirect('/token')

        except Exception as e:
            print(e)

    # Agar request method POST nahi hai to register page render karein
    return render(request, 'register.html')

# success view define karein
def success(request):
    return render(request, 'success.html')

# token_send view define karein
def token_send(request):
    return render(request, 'token_send.html')

# verify view define karein
def verify(request, auth_token):
    try:
        # Auth token ke basis pe profile object filter karein
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()

        # Agar profile_obj mila hai
        if profile_obj:
            # Aur profile verified hai to message show karein aur login page pe redirect karein
            if profile_obj.is_verified:
                messages.success(request, 'Your account has been created.')
                return redirect('/login')

            # Profile verified nahi hai to use verified mark karein aur message show karein
            profile_obj.is_verified = True
            profile_obj.save()
            messages.success(request, 'Your account has been created.')
            return redirect('/login')

        # Agar profile_obj nahi mila to error page pe redirect karein
        else:
            return redirect('/error')

    except Exception as e:
        print(e)
        return redirect('/')

# send_mail_after_registration function define karein
def send_mail_after_registration(email, token):
    subject = 'Your account needs to be verified'
    message = f'Hi, paste the link to verify your account: http://127.0.0.1:8000/verify/{token}'
    email_form = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_form, recipient_list)

# error_page view define karein
def error_page(request):
    return render(request, 'error.html')

def logoutu(request):
    logout(request)
    return HttpResponseRedirect("/register")