from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.cache import cache_page
from .forms import PostForm, CommentForm
from .models import Group, Post, Follow

User = get_user_model()


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = list(
        Post.objects.select_related(
            'group', 'author'
        ).order_by(
            '-pub_date'
        ).all())
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
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
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
    following = Follow.objects.filter(user=request.user, author=user).exists()
    return render(request, 'profile.html', {'user': user,
                                            'request_user': request.user,
                                            'following': following,
                                            'page': page,
                                            'paginator': paginator})


def post_view(request, username, post_id):
    user = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    form = CommentForm()
    following = Follow.objects.filter(user=request.user, author=user).exists()
    return render(request, 'post.html', {'user': user,
                                         'request_user': request.user,
                                         'post': post,
                                         'items': comments,
                                         'form': form,
                                         'following': following,
                                         })


@login_required()
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if request.user != author \
            or request.method not in ("GET", "POST"):  # TODO CHECK THIS
        return redirect('post', username, post_id)

    if not form.is_valid():
        return render(request, 'new_or_edit.html', {'form': form,
                                                    'username': username,
                                                    'post_id': post_id})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('profile', username)


@login_required()
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST)

    if not form.is_valid():
        user = get_object_or_404(User, username=username)
        comments = post.comments.all()
        return render('post.html', {'user': user,
                                    'request_user': request.user,
                                    'post': post,
                                    'items': comments,
                                    'form': form})
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('post', username, post_id)


@login_required
def follow_index(request):
    follows = Follow.objects.filter(user=request.user)
    authors = User.objects.filter(following__in=follows).values('id')
    posts = Post.objects.filter(author_id__in=authors)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(request, "follow.html", {'page': page,
                                           'paginator': paginator})


@login_required
def profile_follow(request, username):
    user = request.user
    author = User.objects.get(username=username)
    if not Follow.objects.filter(user=user, author=author).exists():
        Follow.objects.create(user=user, author=author)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    follow = Follow.objects.filter(user=user, author__username=username)
    if follow.exists:
        follow.delete()
    return redirect('profile', username)


def page_not_found(request, exception):
    return render(request, "misc/404.html",
                  {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)
