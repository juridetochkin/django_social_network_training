from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from .models import Group, Post


def index(request):
    latest = list(Post
                  .objects
                  .all()
                  .select_related("author", "group")
                  [:11])

    return render(request, "index.html", {"posts": latest})


def groups_list(request):
    groups = list(Group.objects.all().values("slug", "title", "description"))
    return render(request, "groups.html", {"groups": groups})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = list(group.posts.all()[:12])
    return render(request, "group.html", {"group": group, "posts": posts})


@login_required()
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "new_post.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")
