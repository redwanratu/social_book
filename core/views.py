from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Profile,Post,LikePost,Follower
from itertools import chain

# Create your views here.
@login_required(login_url='signin')
def index(request):
    #user_profile=Profile.objects.get(username=request.user.username)
    user_profile=Profile.objects.get(user=request.user.id)
    # get all post
    posts=Post.objects.all()

    # customize the feed
    following_user_list=[]
    feeds=[]

    following_user=Follower.objects.filter(follower=request.user.username)

    for following in following_user:
        following_user_list.append(following.user)

    for username in following_user_list:
        users_post=Post.objects.filter(user=username)
        feeds.append(users_post)
    
    feeds=list(chain(*feeds))

    # user suggestions
    user_all=Profile.objects.all()
    user_suggestions=[]
    for user in user_all:
        if user.user.username not in list(following_user_list):
            user_suggestions.append(user)
  
    context={
        'user_suggestions':user_suggestions,
        'user_profile':user_profile,
        'posts': feeds
    }
    return render(request,'index.html',context)

@login_required(login_url='signin')
def upload(request):
    if request.method=='POST':
        
        image_uplaod=request.FILES.get('image_uplaod')
        user=request.user.username
        caption= request.POST['caption']

        new_post=Post.objects.create(user=user,image=image_uplaod,caption=caption)
        new_post.save()        
        
    return redirect('/')

@login_required(login_url='signin')
def like_post(request):
    username=request.user.username
    post_id=request.GET.get('post_id')

    # find the post and change no_of_likes
    post=Post.objects.get(id=post_id)

    # check like post if it liked or not
    like_post= LikePost.objects.filter(post_id=post_id,username=username).first()
    if like_post is None:
        post.no_of_likes=post.no_of_likes + 1
        post.save()
        new_like=LikePost.objects.create(username=username,post_id=post_id)
        new_like.save()
        return redirect("/")

    else:
        post.no_of_likes=post.no_of_likes-1
        post.save()
        like_post.delete()
        return redirect("/")

@login_required(login_url='signin')
def search(request):
    user_profile=Profile.objects.get(user=request.user.id)
    if request.method=='POST':
        username=request.POST['username']
        user_objects=User.objects.filter(username__icontains=username)

        
        search_users=[]
        for user in user_objects:
            search_user=Profile.objects.get(id_user=user.id)
            search_users.append(search_user)
    
        print(search_users)
        
    return render(request,"search.html",{'search_users':search_users,'user_profile':user_profile})

@login_required(login_url='signin')
def profile(request,pk):
    user=User.objects.get(username=pk)
    user_profile=Profile.objects.get(user=user)
    posts=Post.objects.filter(user=user.username)
    post_length=len(posts)

    user=pk
    follower=request.user.username
    #follower count
    follower_count=Follower.objects.filter(user=user).count() 

    #following count
    following_count=Follower.objects.filter(follower=user).count() 

    #follow status
    if Follower.objects.filter(user=user,follower=follower).first():
        follow_status='Unfollow'
    else:
        follow_status='Follow'


    context={
        'user_profile':user_profile,
        'posts': posts,
        'follower_count': follower_count,
        'following_count': following_count,
        'follow_status': follow_status,
        'post_length': post_length,

    }
    return render(request,"profile.html",context)

@login_required(login_url='signin')
def follow(request):
    if request.method=='POST':
        user=request.POST['user']
        follower=request.user.username
        print("hellow")
        follower_filter=Follower.objects.filter(user=user,follower=follower).first()
        if follower_filter is None:
            new_follower=Follower.objects.create(user=user,follower=follower)
            new_follower.save()
        else:
            follower_filter.delete()

        return redirect('/profile/'+user)  
      

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

                # log in user and redirect to the settings page

                user_login=auth.authenticate(username=username,password=password)
                auth.login(request,user_login)


                # add user to Profile Model
                user_model=User.objects.get(username=username)
                new_profile=Profile.objects.create(user=user_model,id_user=user_model.id) 
                new_profile.save()

                return redirect('settings')


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
def settings(request):
    # colect user profile
    user_profile=Profile.objects.get(user=request.user.id)
    
    # collect data from form
    if request.method=='POST':
        bio=request.POST['bio']
        location=request.POST['location']  
        
        if request.FILES.get('image'):
            image=request.FILES.get('image')
        else:
            image= user_profile.profileimg

        user_profile.bio=bio
        user_profile.location=location 
        user_profile.profileimg=image
        
        user_profile.save()
    return render(request,'setting.html',{'user_profile':user_profile})

@login_required(login_url='signin')
def signout(request):
    auth.logout(request)
    return render(request,'signin.html')
 