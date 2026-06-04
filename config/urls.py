from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

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
    path('', include('core.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
