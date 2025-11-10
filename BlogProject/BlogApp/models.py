from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="profile_images/", default="default.png", blank=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

TAG_CHOICES = [
    ("travel", "Travel"),
    ("science", "Science"),
    ("history", "History"),
    ("math", "Math"),
    ("beauty", "Beauty"),
    ("cars", "Cars"),
    ("technology", "Technology"),
    ("entertainment", "Entertainment"),
    ("hollywood", "Hollywood"),
    ("news", "News"),
    ("sports", "Sports"),
]


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)
    def __str__(self):
        return self.name
    
    
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    image = models.ImageField(upload_to="posts/", blank=True, null=True)
    text = models.TextField(blank=True)
    title=models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
   

    def __str__(self):
        return f"{self.author.username} Post"
    
    @property
    def like_count(self):
        return self.likes.count()
    

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        
               
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    likes = models.ManyToManyField(User, related_name="liked_comments", blank=True)

    def __str__(self):
        return f"Comment by {self.user.username}"

    @property
    def like_count(self):
        return self.likes.count()

    @property
    def reply_count(self):
        return self.replies.count()
    
    
    
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")  

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
    

class SavePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        

    
    
    
