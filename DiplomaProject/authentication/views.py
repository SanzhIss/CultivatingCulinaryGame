from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail, EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from . tokens import generate_token

# Create your views here.
def home(request):
    return render(request, "authentication/index.html")


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        pass_reg = request.POST['pass_reg']
        pass_config = request.POST['pass_config']

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist! Try other username")
            return redirect('home')

        # if User.objects.filter(email=email):
        #     messages.error(request, "Email already registered")
        #     return redirect('home')

        if len(username) > 15:
            messages.error(request, "Username must be under 15 characters")

        if pass_reg != pass_config:
            messages.error(request, "Password didn't match!")

        if not username.isalnum():
            messages.error(request, "Username must contain only Numbers and Letters!")
            return redirect('home')

        theuser = User.objects.create_user(username, email, pass_reg)
        theuser.first_name = firstname
        theuser.last_name = lastname
        theuser.is_active = False
        theuser.save()

        messages.success(request, "Your Account has been successfully created! We have sent you a confirmation via "
                                  "email. Please confirm it")

        subject = "[Captivating Culinary GAME] Successful registration"
        message = "Hello " + theuser.first_name + "!! \n" + "Welcome to Captivating Culinary Game \nOnline platform designed as a captivating culinary game! \nWe have sent you a confirmation email. Pсвlease confirm your email in order to activate your account. \n\nThank You for visiting our website! \nAdmin"
        from_email = settings.EMAIL_HOST_USER
        to_list = [theuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently =True)

        current_site = get_current_site(request)
        email_subject = "Confirm your email @ Captivating Culinary Game!"
        message2 = render_to_string('email_confirmation.html',{

            'name': theuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(theuser.pk)),
            'token': generate_token.make_token(theuser)
        })

        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [theuser.email],
        )
        email.fail_silently = True
        email.send()

        return redirect('signin')

    return render(request, "authentication/signup.html")


def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        pass_reg = request.POST['pass_reg']

        theuser = authenticate(username=username, password=pass_reg)

        if theuser is not None:
            login(request, theuser)
            firstname = theuser.first_name
            return render(request, "authentication/index.html", {'firstname': firstname})

        else:
            messages.error(request, "Bad Credentials")
            return redirect('home')

    return render(request, "authentication/signin.html")


def signout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect('home')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        theuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        theuser = None

    if theuser is not None and generate_token.check_token(theuser, token):
        theuser.is_active = True
        theuser.save()
        login(request, theuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')