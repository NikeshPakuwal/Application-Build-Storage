from django.urls import path, include
from rest_framework.decorators import api_view
from .api_view import ApplicationAPI, VersionAPI, RegisterAPI, LoginAPI, UserAPI, LogoutAPI, VersionList, report_api
from rest_framework.authtoken.views import obtain_auth_token
from django.conf import settings
from django.conf.urls.static import static
from .generator import generate_version_pdf


urlpatterns = [

    path('api/v1/application/', ApplicationAPI.as_view(), name='application'),
    path('api/v1/application/<int:pk>/', ApplicationAPI.as_view(), name="application_id"),

    path('api/v1/version/', VersionAPI.as_view(), name='version'),
    path('api/v1/version/<int:pk>/', VersionAPI.as_view(), name="version_id"),

    path('api/v1/register/', RegisterAPI.as_view(), name="register"),
    path('api/v1/login/', LoginAPI.as_view(), name="login"),
    path('api/v1/user/', UserAPI.as_view(), name="user"),
    path('api/v1/logout/', LogoutAPI.as_view(), name="logout"),
    
    path('api/v1/get-token/', obtain_auth_token, name="get_token"),
    
    path('api/v1/version/list/', VersionList.as_view(), name="version_list"),

    path('api/v1/generate/', report_api, name="generate_pdf")

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
    document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT)