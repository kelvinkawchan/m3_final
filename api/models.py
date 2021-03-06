from django.contrib.auth.models import AbstractUser
from django.db import models


NON = "NO"
AWS = "AW"
REACT = "RC"
NODE = "NJ"
UXUI = "UX"
SECURE = "SC"
AZURE = "AZ"
TAG_CHOICES = [
    (NON, "None"),
    (AWS, "AWS"),
    (REACT, "React"),
    (NODE, "NodeJS"),
    (UXUI, "UX/UI"),
    (SECURE, "Security"),
    (AZURE, "Azure"),
]


class User(AbstractUser):
    is_mentor = models.BooleanField(default=False)
    likes = models.ManyToManyField("Post", related_name="likes", blank=True)
    tags = models.CharField(
        max_length=2,
        choices=TAG_CHOICES,
        default=NON,
    )
    is_available = models.BooleanField(default=True)


class Post(models.Model):
    title = models.CharField(max_length=55, blank=False)
    content = models.TextField(max_length=255, blank=False)
    creation_time = models.DateTimeField(auto_now_add=True)
    poster = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="student_posts")
    mentor = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="mentor")
    tags = models.CharField(
        max_length=2,
        choices=TAG_CHOICES,
        default=NON,
    )
    is_answered = models.BooleanField(default=False)


class Comment(models.Model):
    content = models.TextField(max_length=150)
    creation_time = models.DateTimeField(auto_now_add=True)
    commentor = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="user_comments")
    post_connected = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="post_comments")
