from django.contrib import admin
from django.urls import path, include
from .views import  liste_candidats, login_view
from django.conf.urls.static import static
from django.conf import settings
from . import views
from django.views.generic.base import RedirectView
from pages import views
from pages.views import home_page_view
from pages.views import home_page_view, count_view, logout_view

urlpatterns = [
    path('login/', views.login_view, name='login'),
        path('', RedirectView.as_view(url='/pages/login/', permanent=False)),  # ← redirection racine

    path('liste-candidats/', liste_candidats, name='liste_candidats'),
    path('pages/', include('pages.urls')),  # Inclusion de toutes les urls de l'app pages
        path('pages/ajout-offre/', views.ajout_offre, name='ajout_offre'),
    path('', home_page_view, name='home'),
    path("", include("chatbot.urls")),

  

 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
