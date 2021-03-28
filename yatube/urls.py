import debug_toolbar
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("about/", include("django.contrib.flatpages.urls")),
    path("auth/", include("users.urls")),
    path("auth/", include("django.contrib.auth.urls")),
    path('__debug__/', include(debug_toolbar.urls)),
    ]


# Flatpages
urlpatterns += [
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='about-author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='about-spec')
    ]


# Posts App Urls
urlpatterns += [
    path("", include("posts.urls")),
    ]
