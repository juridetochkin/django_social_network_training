from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.new_post, name="new_post"),
    path("group/<slug:slug>/", views.group_posts),
    path("group/", views.groups_list)
         ]
