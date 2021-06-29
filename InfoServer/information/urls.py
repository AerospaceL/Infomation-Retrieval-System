from django.urls import path, re_path

from .import views

urlpatterns = [
    path('search/', views.search, name='search'),
    path('extract/', views.extract, name='extract'),
    path('upload/', views.upload, name='upload'),
    path('submit/', views.submit, name='submit'),

    re_path(r'^static/(?P<path>.*)$', views.download, name="download")
]
