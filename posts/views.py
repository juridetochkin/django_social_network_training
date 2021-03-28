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
    page_number = request.GET.get('page')    # переменная в URL с номером запрошенной страницы
    page = paginator.get_page(page_number)   # получить записи с нужным смещением
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
    user = User.objects.get(username=username)
    post_list = Post.objects.filter(author=user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'user': user,
                                            'request_user': request.user,
                                            'page': page,
                                            'paginator': paginator})


def post_view(request, username, post_id):
    user = User.objects.get(username=username)
    post = Post.objects.get(id=post_id)
    return render(request, 'post.html', {'user': user,
                                         'request_user': request.user,
                                         'post': post})


def post_edit(request, username, post_id):
    post = Post.objects.get(id=post_id)
    author = post.author
    if request.user == author:
        if request.method == "GET":
            form = PostForm(instance=post)
            return render(request, 'new_or_edit.html', {'form': form,
                                                        'username': username,
                                                        'post_id': post_id})
        elif request.method == "POST":
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                post = form.save(commit=False)
                post.author = request.user
                post.save()
                return redirect('profile', username)
            else:
                return render(request,
                              'new_or_edit.html',
                              {'form': form,
                               'username': username,
                               'post_id': post_id})
    return redirect('post', username, post_id)
