from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render


def handler400(request, exception=None):
    return render(request, '400.html', status=400)

def handler403(request, exception=None):
    return render(request, '403.html', status=403)

def handler404(request, exception=None):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('lessons/', include('lessons.urls')),
    path('vocabulary/', include('vocabulary.urls')),
    path('grammar/', include('grammar.urls')),
    path('quiz/', include('quiz.urls')),
    path('progress/', include('progress.urls')),
    path('hangul/', include('hangul.urls')),
    path('review/', include('review.urls')),
    path('library/', include('library.urls')),
    path('api/', include('api.urls')),
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
