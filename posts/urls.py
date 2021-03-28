from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_post, name="new_post"),
    path("group/<slug:slug>/", views.group_posts),
    path("group/", views.groups_list),
    path('<str:username>/', views.profile, name='profile'),               # Users profile page
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),  # Users post page
    path('<str:username>/<int:post_id>/edit/',                            # Users post edit page
         views.post_edit,
         name='post_edit'),
         ]
