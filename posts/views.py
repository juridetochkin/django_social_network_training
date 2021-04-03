from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from .forms import PostForm
from .models import Group, Post

User = get_user_model()


def index(request):
    post_list = list(Post.objects.order_by('-pub_date').all())
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "index.html",
                  {'page': page,
                   'paginator': paginator})


def groups_list(request):
    groups = list(Group.objects.all().values("slug", "title"))
    paginator = Paginator(groups, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request,
                  "groups.html",
                  {"groups": groups,
                   "page": page,
                   "paginator": paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "group.html",
                  {"group": group,
                   "page": page,
                   "paginator": paginator})


@login_required()
def new_post(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, "new_or_edit.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(author=user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'user': user,
                                            'request_user': request.user,
                                            'page': page,
                                            'paginator': paginator})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post.html', {'user': user,
                                         'request_user': request.user,
                                         'post': post})


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    form = PostForm(request.POST or None, instance=post)

    if request.user != author \
            or request.method not in ("GET", "POST"):
        return redirect('post', username, post_id)

    if not form.is_valid():
        return render(request, 'new_or_edit.html', {'form': form,
                                                    'username': username,
                                                    'post_id': post_id})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('profile', username)


def page_not_found(request, exception):  # Check exception
    # 'exception' var is only received by the func, and not returned
    return render(request, "misc/404.html",
                  {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
