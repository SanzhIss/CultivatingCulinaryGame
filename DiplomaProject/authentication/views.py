from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect


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

        theuser = User.objects.create_user(username, email, pass_reg)
        theuser.first_name = firstname
        theuser.last_name = lastname

        theuser.save()

        messages.success(request, "Your Account has been successfully created!")

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
