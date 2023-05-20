"""VR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.urls import path
from VR import settings
import app.views

urlpatterns = [
                  path('', app.views.home),
                  path('uploaddataset', app.views.uploadataset),
                  path('viewdataset', app.views.viewdataset),
                  path('groupstat', app.views.groupstat),
                  path('activemembers', app.views.activemembers),
                  path('activemonths', app.views.activemonths),
                  path('activedays', app.views.activedays),
                  path('activetimes', app.views.activetimes),
                  path('wordcloud', app.views.wordcloud),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
