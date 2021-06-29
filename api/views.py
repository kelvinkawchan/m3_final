import json

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from .models import User, Post


def show_posts(title, request, posts, profile=None):

    # Get current page of psots
    page_index = request.GET.get("page", 1)
    paginator = Paginator(posts, 10)
    page = paginator.page(page_index)

    if profile is None or (not request.user.is_mentor):
        mentor = False
    else:
        mentor = True

    # Show posts page
    return render(request, "api/index.html", {
        "title": title,
        "page": page,
        "profile": profile,
        "is_mentor": mentor,
        "show_new_post": (
            request.user.is_authenticated and
            (profile is None or profile == request.user) and
            (not request.user.is_mentor)
        ),
    })


def index(request):
    posts = Post.objects.order_by("-creation_time").all()
    return show_posts("All Posts", request, posts)


@login_required
def edit(request, post_id):
    if request.method == "PUT":
        # Query for post
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return JsonResponse({"error": "Post not found."}, status=404)

        # Only let the poster edit the post
        if post.poster != request.user:
            return JsonResponse({"error": "Forbidden."}, status=403)

        # Update post body
        data = json.loads(request.body)
        post.content = data["content"]
        post.save()
        return JsonResponse({
            "id": post_id,
            "content": post.content,
            "likes": post.likes.count()
        })


@login_required
def new_post(request):
    if request.method == "POST":
        p = Post(
            title=request.POST["title"],
            content=request.POST["content"],
            tags=request.POST["tags"],
            poster=request.user
        )
        print(request.POST["tags"])
        p.save()
        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", reverse("index"))
        )


@login_required
def post(request, post_id):
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "Post not found."}, status=404)

    # Update whether post is liked or not
    if request.method == "PUT":
        data = json.loads(request.body)
        like = bool(data.get("like"))
        if like:
            request.user.likes.add(post)
        else:
            request.user.likes.remove(post)

    return JsonResponse({
        "id": post_id,
        "content": post.content,
        "likes": post.likes.count()
    })


def user(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User does not exist.")
    posts = Post.objects.filter(poster=user).order_by("-creation_time").all()
    return show_posts(user.username, request, posts, profile=user)


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "api/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "api/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        if email[-14:] == "@accenture.com":
            mentor = True
        else:
            mentor = False

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "api/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(
                username, email, password,
                is_mentor=mentor
            )
            user.save()
        except IntegrityError:
            return render(request, "api/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "api/register.html")
