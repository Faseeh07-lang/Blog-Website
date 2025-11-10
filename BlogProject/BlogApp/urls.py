from django.urls import path
from .views import mainpage,LoginView,MainPage,user_logout,SignupView,ProfileView,EditProfileView,PostCreateView,HomeView, FollowUserView,VisitProfile,showfollower,showfollowing,send_test_email, Save_post,show_save_post
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', mainpage, name="main"),
    path('login/', LoginView.as_view(), name="login"),
    path('signup/',SignupView.as_view(), name="signup"),
    path('profile/',ProfileView.as_view(), name='profile'),
    path('logout/',user_logout, name="logout"),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path('post/create/', PostCreateView.as_view(), name='create_post'),
    path('like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path('home/', HomeView.as_view(), name='home'),
    path('follow/<int:user_id>/', FollowUserView.as_view(), name='follow_user'),
    path('user/<int:user_id>/', views.VisitProfile, name='VisitProfile'),
    path('follower/<int:user_id>/',showfollower , name='all_followers'),
    path('following/<int:user_id>/',showfollowing , name='all_following'),
    path('comment/<int:comment_id>/like/', views.like_comment, name='like_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('savepost/<int:post_id>/', views.Save_post, name="save_post"),
    path('show_save_post/',views.show_save_post,name="show_saved_post"),
    path('delete_account/', views.delete_account, name='delete_account'),

    path("send-email/", send_test_email),
    path('reset_password/', 
        auth_views.PasswordResetView.as_view(template_name="password_reset.html"), 
        name="reset_password"),

    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), 
        name="password_reset_done"),

    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_form.html"), 
        name="password_reset_confirm"),

    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_done.html"), 
        name="password_reset_complete"),
    
]
