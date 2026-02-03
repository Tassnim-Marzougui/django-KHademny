from django.urls import path 
from . import views

#domain.com/website/...

urlpatterns = [
    path('',view.home_view, name='home'),
    path('about',views.about_view, name='about'),
]

