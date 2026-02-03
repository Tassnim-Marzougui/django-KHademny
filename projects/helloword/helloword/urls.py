from django.contrib import admin
from django.urls import path, include
from pages.views import home_page_view, logout_view
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),

    # Page d'accueil
    path('', home_page_view, name='home'),
    path("", include("pages.urls")),   # ✅ ça inclut toutes les routes de ton app
    # Page compte / liste offres

    # Pages de l'application "pages"
    path('pages/', include('pages.urls')),

    # Logout
    path('logout/', logout_view, name="logout"),

    # Autres apps
    path('', include('meeting.urls')),
    path('entreprises/', TemplateView.as_view(template_name='entreprises.html'), name='entreprises'),


    
]
