from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile

# Create your views here.
@login_required(login_url='signin')
def index(request):
    return render(request,'index.html')

def signup(request):
    # check if request is POST method or redirect to sign up page
    if request.method=='POST':
        username=request.POST['username']
        email=request.POST['email']
        password=request.POST['password']
        password_confirm=request.POST['password2']

        # check if password match
        if password == password_confirm:
            # check if user with email exists
            if User.objects.filter(email=email).exists():
                messages.info(request,'Email taken')
                return redirect('signup') 
            
            # check if user with username exists
            elif User.objects.filter(username=username).exists():
                messages.info(request,'Username taken')
                return redirect('signup')

            # save user
            else:
                # add user to Admin user
                user= User.objects.create_user(username=username,email=email,password=password)
                user.save()

                # add user to Profile Model
                user_model=User.objects.get(username=username)
                new_profile=Profile.objects.create(user=user_model,id_user=user_model.id) 
                new_profile.save()

                return redirect('signup')


        else:
            messages.info(request,'Password Not matches')
            return redirect('signup')


    else:
        return render(request,'signup.html')


def signin(request):
    if request.method=='POST':
        username= request.POST['username']
        password= request.POST['password']

        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Credential not match')
            return redirect('signin')


    else:

        return render(request,'signin.html')

@login_required(login_url='signin')
def signout(request):
    auth.logout(request)
    return render(request,'signin.html')
 