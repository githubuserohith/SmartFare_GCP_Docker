from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from .otp import email_otp, booking_confirmation, forgot_pwd_email
from django.contrib.auth.hashers import check_password
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import *
from django.urls import reverse
from dotenv import load_dotenv
import os
from .get_pics import fn_getpics
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import base64
from datetime import datetime, date, time
from .face_recog import fn_facetrain, fn_facepred
# from django.utils import timezone
import datetime
import warnings

warnings.filterwarnings('ignore')

load_dotenv()

# Access your API key from the environment variables
stripe.api_key = os.getenv("stripe_secret_key")
stripe_pub_key = os.getenv("stripe_pub_key")

# Now you can use the API key in your code
# print("stripe API Key:", stripe.api_key)

class UserRegForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# get pics
@login_required
def register(request):
    username = request.session['username']
    if request.method == "POST":
        if request.POST.get('register') == 'registered':
            op = fn_getpics(username,request)
            if op:
                messages.success(request, "Registered successfully. Training.....")
            fn_facetrain()
            messages.success(request, "Training completed")

    return render(request, 'register.html',{'username':username})


def fn_start_time(board_list):
    for name in board_list:
        Fare.objects.create(username=name,
                            start_time=datetime.datetime.now(),
                            end_time = datetime.datetime.now(),
                            duration=0
                            )

def fn_end_time(deboard_list):
    for name in deboard_list:
        Fare.objects.filter(username=name,duration=0).update(end_time=datetime.datetime.now())


def fn_calc_duration(deboard_list,board_list,request):
    for name in deboard_list:
        if name in board_list:
            fare_obj = Fare.objects.filter(username=name,duration=0).first()
            end = fare_obj.end_time
            start = fare_obj.start_time
            d = (end-start).total_seconds()/60
            Fare.objects.filter(username=name,duration=0).update(duration=d)
            fn_fare_calc(name,d,request)
        else:
            messages.error(request, f"{name} did not board")


def fn_fare_calc(name,duration,request):
    wallet_amt = Wallet.objects.filter(username=name).first().amount
    # if wallet_amt>0:
    charge = duration
    updated_amt= wallet_amt-charge
    Wallet.objects.filter(username=name).update(amount=updated_amt)
    # else:
    #     messages.success(request, "no charges")


# for admins
@login_required
def admin(request):
    user_name = request.session['username']
    superuser = User.objects.filter(username=user_name).first()
    op=None
    # boarding_names, deboarding_names = [],[]
    if superuser.is_superuser:    
        if request.POST.get("board_cam")=="start":
            request.session['boarding_names'] = fn_facepred()
            fn_start_time(request.session['boarding_names'])
        elif request.POST.get("deboard_cam")=="start":
            request.session['deboarding_names'] = fn_facepred() 
            fn_end_time(request.session['deboarding_names'])
            fn_calc_duration(request.session['deboarding_names'], request.session['boarding_names'],request)
    else:
        messages.error(request, "Only admins can use this section") 
        return redirect('logout_view')
    
    # Pass the recognized names (if available) to the template context
    # context = {
    #     'recognized_names': op if op else []
    # }
    
    return render(request, 'admin.html', {'boarding_names':request.session.get('boarding_names'),
                                          'deboarding_names':request.session.get('deboarding_names')
                                          })


@login_required
def payment(request):
    amount = request.POST.get('amount')
    wallet_amt = 0  # Define wallet_amt with a default value
    
    if request.method == 'POST': 
        if int(amount)>=100:
                
            customer = stripe.Customer.create(email=request.session['email'],
                                                name=request.session['username'],
                                                source=request.POST['stripeToken']
                                            )
            charge = stripe.PaymentIntent.create(
                customer=customer,
                amount=request.POST.get('amount'),
                currency='inr',
                description='smartfare'
                )

            wallet_user = Wallet.objects.filter(username=request.session['username']).first()
            if wallet_user: 
                old_amount = wallet_user.amount
                # wallet_amount = wallet_instance.amount
                current_amount = request.POST.get('amount')
                new_amount = int(old_amount) + int(current_amount)
                Wallet.objects.filter(username=request.session['username']).update(amount=new_amount)
            else: 
                wallet = Wallet.objects.create(username=request.session['username'], 
                                            email=request.session['email'], 
                                            amount=amount)
                wallet.save()
            messages.success(request, f"Payment of Rs {amount} successfull")   
            return redirect('wallet')
        else:
            messages.error(request, "Payment failed. Minimum amount is Rs 100")
    
        # messages.error(request, "Amount should be greater than Rs 100")

    return render(request, 'payment.html', {'stripe_pub_key':stripe_pub_key})


@login_required
def wallet(request):
    wallet_balance = 0  # Default value if no wallet balance is found
    wallet_instance = Wallet.objects.filter(username=request.session['username']).first()
    if wallet_instance:
        wallet_balance = wallet_instance.amount
    return render(request, 'wallet.html', {'wallet_balance': wallet_balance})


def successMsg(request, args):
	amount = args
	return render(request, 'success.html', {'amount':amount})

def failureMsg(request, args):
	amount = args
	return render(request, 'failure.html', {'amount':amount})


def layout(request):
    return render(request, 'layout.html')

def login_view(request):
    if request.method == 'POST':
        if request.POST.get('submit_login') == 'submitted':
            username = request.POST.get('username')
            password = request.POST.get('password')

            # u = request.session.get('Username')
            user_obj = User.objects.filter(username=username).first()
            if user_obj:
                request.session['email'] = user_obj.email
                pwd_otp = request.session.get('otp')
                otp_username = request.session.get('otp_username')
                u = User.objects.filter(username=username).first()
                user = authenticate(username=username, password=password)
            else:
                messages.error(request, "Username does not exist")
                return redirect('login_view')
            if u:
                if user:
                    login(request, user)
                    request.session['username'] = username
                    messages.success(request, f" Logged in successfully ")
                    return redirect('register')
                else:
                    messages.error(request, "Incorrect password")
            else:
                messages.error(request, "Username is incorrect or does not exist")
    return render(request, 'login_view.html')


def signup(request):
    form = UserRegForm()
    if request.method == "POST":
        form = UserRegForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password1')
        cnf_password = request.POST.get('password2')
        user_email = request.POST.get('email')
        e = User.objects.filter(email=user_email).first()
        if password != cnf_password:
            messages.error(request, "Passwords do not match. Please try again")
            form = UserRegForm()
        elif e:
            messages.error(request, "Email address already exists. Try again.")
            form = UserRegForm()
        elif form.is_valid():
            n = User.objects.create_user(username=username, password=password, email=user_email)
            n.save()
            messages.success(request, f"Account created for {username}. Please login.")
            return redirect('login_view')

    return render(request, 'signup.html', {'form': form})

@login_required
def logout_view(request):
    # if request.method == "POST":
    username = request.session.get('username')
    u = User.objects.filter(first_name='OTP', username=username).first()
    if u:
        u.delete()
    logout(request)
    # return render(request, 'logout_view.html')
    messages.success(request, "Logged out successfully")
    return redirect('login_view')


def forgot_pwd(request):
    if request.method == "POST" and request.POST.get('forgot_pwd'):
        e = request.POST.get('email_name')
        u = User.objects.filter(email=e).first()
        if u:
            username = u.username
            otp_str = str(forgot_pwd_email(u.email, u.username))
            u.delete()
            # print(f"{u.username} is deleted from db")
            new_u = User.objects.create_user(username=username, password=otp_str, email=e)
            # print(f"{u.username} is deleted from db")
            new_u.save()
            # print(f"{new_u} is saved to db")
            messages.success(request, f" OTP sent to email address: {e}")
            return redirect('login_view')
        else:
            messages.error(request, "Entered email address does not exist. Please Sign up.")

    return render(request, 'forgot_pwd.html')


def otp(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        u = User.objects.filter(username=username).first()
        if u:
            messages.error(request, f" Username: '{username}' already exists. Try another.")
            return redirect('otp')
        else:
            request.session['otp_username'] = username
            otp = str(email_otp(email, username))
            request.session['otp'] = otp
            n = User.objects.create_user(username=username, password=otp, first_name='OTP', email=email)
            n.save()
            messages.success(request, f" OTP sent to email address: {email}")
            return redirect('login_view')

    return render(request, 'otp.html')

@login_required
def change_pwd(request):
    username = request.session.get('username')
    user = User.objects.get(username=username)
    if user.first_name == "OTP":
        messages.error(request, "Users logged in with OTP cannot change password. Please sign up.")
        return redirect('search')
    else:
        old_pwd = request.POST.get('old_pwd')
        new_pwd1 = request.POST.get('new_pwd1')
        new_pwd2 = request.POST.get('new_pwd2')
        if request.method == "POST":
            if request.POST.get('change_pwd'):
                if check_password(old_pwd, user.password):
                    if new_pwd1 == new_pwd2:
                        if old_pwd != new_pwd1:
                            user.set_password(new_pwd1)
                            user.save()
                            messages.success(request, "Password changed successfully. Login again")
                            return redirect('login_view')
                        else:
                            messages.error(request, "Old and new passwords are same. Try again")
                            return redirect('change_pwd')

                    else:
                        messages.error(request, "New passwords does not match. Try again")
                        return redirect('change_pwd')
                else:
                    messages.error(request, "Incorrect old password. Try again")
                    return redirect('change_pwd')

    return render(request, 'change_pwd.html')



