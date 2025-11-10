from django import forms
from .models import Profile,Post

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'placeholder': 'Write something about yourself...', 'rows':4}),
        }
        

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'image']  # include title field
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter post title',
                'required': True
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Write your post...'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            })
        }