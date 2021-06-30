from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("post", views.new_post, name="new_post"),
    path("posts/<int:post_id>", views.post, name="post"),
    path("posts/<int:post_id>/edit", views.edit, name="edit"),
    path("register", views.register, name="register"),
    path("users/<str:username>", views.user, name="user"),
    path("free/<str:username>", views.free, name="free"),
    path("busy/<str:username>", views.busy, name="busy"),
]
