from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views import View
from django.contrib.auth.models import User
from .forms import ProfileForm,PostForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Profile,Post,Like,Comment,Follow,SavePost
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.http import HttpResponse,HttpResponseForbidden



def mainpage(request):
    context={"data":"Welcome to My Blog, a space where ideas, stories, and insights come together. Here, you’ll find posts on a variety of topics including technology, programming, personal growth, and more. Whether you’re looking to learn something new, get inspired, or just enjoy thoughtful articles, you’ll find something for everyone. Dive in, explore the posts, and don’t forget to share your thoughts — your engagement makes this community vibrant and meaningful!"}
    return render(request, "main_page.html", context)



class LoginView(View):
    template_name = "login.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('profile')  
        else:
            messages.error(request, "Invalid username or password")
            return redirect('login')


class SignupView(View):
    template_name = "signup.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            return redirect('signup')

        if User.objects.filter(username=username).exists():
            return redirect('signup')

        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
   
        return redirect('profile')  


def user_logout(request):
    logout(request)
   
    return redirect("login")

class EditProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        context = {'profile': profile}
        return render(request, 'edit_profile.html', context)

    def post(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        
        image = request.FILES.get('image')
        bio = request.POST.get('bio')  

        if image:
            profile.image = image
        
        profile.bio = bio  
        profile.save()

        return redirect('profile')


class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        posts = Post.objects.filter(author=request.user).order_by("-created_at").prefetch_related('likes', 'comments')
        liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
        followers = Follow.objects.filter(following=request.user).select_related('follower')
        following = Follow.objects.filter(follower=request.user).select_related('following')

        context = {
            "profile": profile,
            "posts": posts,
            "liked_post_ids": liked_post_ids,
            "followers": followers,
            "following": following,
        }
        return render(request, "profile.html", context)
    
    
@method_decorator(login_required, name='dispatch')
class MainPage(View):
    def get(self, request):
        return render(request, "main_page.html")
    
    
class PostCreateView(LoginRequiredMixin, View):
    template_name = "create_post.html"

    def get(self, request):
        form = PostForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("profile")
        return render(request, self.template_name, {"form": form})
    
    
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True

    return JsonResponse({
        "liked": liked,
        "like_count": post.likes.count()
    })



@login_required
def add_comment(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        text = request.POST.get("text")
        parent_id = request.POST.get("parent_id")
        parent_comment = Comment.objects.get(id=parent_id) if parent_id else None
        Comment.objects.create(user=request.user, post=post, text=text, parent=parent_comment)
        return redirect("profile")
    
class HomeView(LoginRequiredMixin, View):
    login_url = 'login'  # redirect if user not logged in

    def get(self, request):
        # Get all profiles except the current user for the sidebar
        profiles = Profile.objects.exclude(user=request.user)

        # Get IDs of users the current user is following
        following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)

        # Get posts from followed users only, most recent first
        posts = Post.objects.filter(author_id__in=following_ids).order_by("-created_at").prefetch_related('likes', 'comments')

        context = {
            "profiles": profiles,
            "posts": posts,
            "following_ids": following_ids,
        }
        return render(request, "home.html", context)
    
    
class FollowUserView(LoginRequiredMixin, View):
    def post(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        
        if target_user == request.user:
            return redirect('home')

        existing_follow = Follow.objects.filter(follower=request.user, following=target_user)
     
        if existing_follow.exists():
            existing_follow.delete()
        else:
            Follow.objects.create(follower=request.user, following=target_user)
        return redirect('home')
    
    
    
def VisitProfile(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)
    posts = Post.objects.filter(author=profile.user).order_by('-created_at')
    followers = Follow.objects.filter(following=profile.user)
    following = Follow.objects.filter(follower=profile.user)
    

    if request.user.is_authenticated:
        liked_post_ids = Like.objects.filter(user=request.user).values_list('post_id', flat=True)
    else:
        liked_post_ids = []

    context = {
        'profile': profile,
        'posts': posts,
        'followers': followers,
        'following': following,
        'liked_post_ids': liked_post_ids,
        'is_own_profile': request.user.id == profile.user.id,  # hide edit/create buttons
    }
    return render(request, 'visitProfile.html', context)



def showfollower(request, user_id):
    following = Follow.objects.filter(follower_id=user_id)
    return render(request, "followers.html", {"following": following})


def showfollowing(request, user_id):
    following = Follow.objects.filter(following_id=user_id)
    return render(request, "following.html", {"following": following})



def send_test_email(request):
    send_mail(
        'Hello from Django!',
        'This is a test email.',
        'yourgmail@gmail.com',       
        ['mf1.rehman@gmail.com'],    
        fail_silently=False,
    )
    return HttpResponse("Email sent!")


@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user

    if user in comment.likes.all():
        comment.likes.remove(user)
    else:
        comment.likes.add(user)

    return redirect(request.META.get('HTTP_REFERER', 'home'))


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        comment.delete()
    else:
        return HttpResponseForbidden("You cannot delete this comment.")
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def Save_post(request, post_id):
    if request.method=="POST":
        SavePost.objects.create(user=request.user, post=post_id)
        
@login_required
def Save_post(request, post_id):
    if request.method == "POST":
        save_post, created = SavePost.objects.get_or_create(
            user=request.user,
            post_id=post_id
        )

        if not created:
            save_post.delete()
            saved = False
        else:
            saved = True

        return JsonResponse({"status": saved})
    
@login_required
def show_save_post(request):
    saved_posts = SavePost.objects.filter(user=request.user).order_by('-saved_at')
    context = {
        'saved_posts': saved_posts
    }
    return render(request, 'save_post.html', context)


@login_required
def delete_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)
        user.delete()
        return JsonResponse({"deleted": True})
        
        