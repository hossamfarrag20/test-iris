from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from pages.models import nprofile
from django.contrib.auth.tokens import default_token_generator  #Reset Password Tonken
from django.urls import reverse 
from django.template.loader import render_to_string 
import logging #render Issue
import urllib.parse #Reset Password
from django.contrib.auth import update_session_auth_hash     #Change Password

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def signup(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        is_doctor = request.POST.get('is_doctor')  # This will be 'on' if the checkbox is checked

        # Check if username is taken
        if User.objects.filter(username=uname).exists():
            error_message = "Username is already taken. Please choose a different one."
            return render(request, 'signup/signup.html', {'error_message': error_message})

        # Check if email is taken
        if User.objects.filter(email=email).exists():
            error_message = "Email is already in use. Please choose a different one."
            return render(request, 'signup/signup.html', {'error_message': error_message})

        # Check if passwords match
        if password != confirm_password:
            error_message = "Passwords do not match."
            return render(request, 'signup/signup.html', {'error_message': error_message})

        # Check password strength
        if len(password) < 8:
            error_message = "Password must be at least 8 characters long."
            return render(request, 'signup/signup.html', {'error_message': error_message})

        if not any(char.isdigit() for char in password):
            error_message = "Password must contain at least one digit."
            return render(request, 'signup/signup.html', {'error_message': error_message})

        if not any(char.isupper() for char in password):
            error_message = "Password must contain at least one uppercase letter."
            return render(request, 'signup/signup.html', {'error_message': error_message})

        # Create user if all checks pass
        muser = User.objects.create_user(username=uname, email=email, password=password)
        muser.save()

        # Optionally create a profile for the user and set is_doctor
        profile = nprofile(usr=muser, is_doctor=is_doctor == 'on')
        profile.save()

        return redirect('index')

    return render(request, 'signup/signup.html', {})



 
 
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request,user)
            # the user is authenticated, redirect to a success page
            return redirect('index')
        else:
            error_message = "Username or Password is not correct."
            return render(request, 'signup/signin.html', {'error_message': error_message})
   
    return render(request, 'signup/signin.html', {})
  
  
def index(request):
    return render(request, 'home/index.html', {})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        docname = request.POST.get('docname')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        full_message = f"Message from : {name}\nPhone Number :{number}\nThe Message : {message}\nDoctor Name: {docname}"
        
        from_email = f"{name} <{settings.EMAIL_HOST_USER}>"
        
        try:
            send_mail(
                subject,
                full_message,
                from_email,
                [email],
                fail_silently=False,
            )
            messages.success(request, 'Thank you for your message, we wii call you back in hour.')
        except Exception as e:
            messages.error(request, 'An error occurred while sending the message. Please try again later.')
        
        return redirect('contact')

    doctors = User.objects.filter(profile__is_doctor=True)
    return render(request, 'home/contact.html', {'doctors': doctors})






@login_required(login_url='signin')
def logoutpage(request):
    logout(request)
    return redirect('index')
        
        
def reset_password(request):
    if request.method == 'POST':
        uid = request.POST.get('uid')
        token = request.POST.get('token')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        logger.debug(f"POST uid: {uid}")
        logger.debug(f"POST token: {token}")

        if not uid or not token:
            error_message = "Missing UID or token."
            logger.error(error_message)
            return render(request, 'signup/reset_password.html', {'error_message': error_message, 'uid': uid, 'token': token})

        if password != confirm_password:
            error_message = "Passwords do not match."
            logger.error(error_message)
            return render(request, 'signup/reset_password.html', {'error_message': error_message, 'uid': uid, 'token': token})

        if len(password) < 8:
            error_message = "Password must be at least 8 characters long."
            logger.error(error_message)
            return render(request, 'signup/reset_password.html', {'error_message': error_message, 'uid': uid, 'token': token})

        if not any(char.isdigit() for char in password):
            error_message = "Password must contain at least one digit."
            logger.error(error_message)
            return render(request, 'signup/reset_password.html', {'error_message': error_message, 'uid': uid, 'token': token})

        if not any(char.isupper() for char in password):
            error_message = "Password must contain at least one uppercase letter."
            logger.error(error_message)
            return render(request, 'signup/reset_password.html', {'error_message': error_message, 'uid': uid, 'token': token})

        try:
            user = User.objects.get(pk=uid)
            logger.debug(f"User found: {user.username}")

            if default_token_generator.check_token(user, token):
                user.set_password(password)
                user.save()
                messages.success(request, 'Password has been successfully changed.')
                logger.info(f"Password for user {user.username} has been successfully changed.")
                return redirect('signin')
            else:
                error_message = "Invalid token."
                logger.error(error_message)
                return render(request, 'signup/reset_password.html', {'error_message': error_message, 'uid': uid, 'token': token})
        except User.DoesNotExist:
            error_message = "Invalid user."
            logger.error(error_message)
            return render(request, 'signup/reset_password.html', {'error_message': error_message, 'uid': uid, 'token': token})

    uid = request.GET.get('uid')
    token = request.GET.get('token')

    logger.debug(f"GET uid: {uid}")
    logger.debug(f"GET token: {token}")

    return render(request, 'signup/reset_password.html', {'uid': uid, 'token': token})

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            reset_url = request.build_absolute_uri(reverse('reset_password') + f'?uid={user.pk}&token={urllib.parse.quote(token)}')

            subject = 'Password Reset Request'
            message = render_to_string('signup/password_reset_email.html', {'reset_url': reset_url})
            from_email = settings.DEFAULT_FROM_EMAIL

            send_mail(subject, message, from_email, [email])

            return render(request, 'signup/password_reset_done.html')

        else:
            error_message = "No user found with this email address."
            return render(request, 'signup/forgetpass.html', {'error_message': error_message})

    return render(request, 'signup/forgetpass.html')

@login_required(login_url='signin')
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('create_new_password')
        confirm_password = request.POST.get('confirm_password')

        if not request.user.check_password(old_password):
            error_message = "Old password is incorrect."
            return render(request, 'signup/change_password.html', {'error_message': error_message})

        if new_password != confirm_password:
            error_message = "New passwords do not match."
            return render(request, 'signup/change_password.html', {'error_message': error_message})

        if len(new_password) < 8:
            error_message = "Password must be at least 8 characters long."
            return render(request, 'signup/change_password.html', {'error_message': error_message})

        if not any(char.isdigit() for char in new_password):
            error_message = "Password must contain at least one digit."
            return render(request, 'signup/change_password.html', {'error_message': error_message})

        if not any(char.isupper() for char in new_password):
            error_message = "Password must contain at least one uppercase letter."
            return render(request, 'signup/change_password.html', {'error_message': error_message})

        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)  # Important!

        messages.success(request, 'Password has been successfully changed.')
        return redirect('index')

    return render(request, 'signup/change_password.html')