from django.contrib import admin
from django.conf import settings
from django.urls import path, include, re_path
from django.conf.urls import url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Gocreate API",
        default_version='v1',
        description="API Documentation for Gocreate",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="bellotobiloba01@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/sso/', include('sso.urls')),

    path('api/v1/songs/', include('songs.urls')),
    path('api/v1/adverts/', include('adverts.urls')),
    path('api/v1/payouts/', include('payouts.urls')),
    path('api/v1/royalty/', include('royalty.urls')),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/systemcontrol/', include('systemcontrol.urls')),
    path('api/v1/subscriptions/', include('subscriptions.urls')),

    url(r'^api/docs/swagger/$', schema_view.with_ui('swagger',
                                                    cache_timeout=0), name='schema-swagger-ui'),
    url(r'^api/docs/redoc/$', schema_view.with_ui('redoc',
                                                  cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

urlpatterns += [re_path('.*',
                        TemplateView.as_view(template_name='frontend/index.html')), ]
