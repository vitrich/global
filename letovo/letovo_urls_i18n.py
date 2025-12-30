from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = []

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path("grade5/", include("grade5.urls")),
    path('', include('cms.urls')),   # стартовый URL — корень сайта
    path('assignments/', include('assignments.urls')),
)
