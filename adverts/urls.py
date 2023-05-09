from django.urls import path

from .views import (
    PlanListAPIView,
    AllAdvertsAPIView,
    PlanDetailsAPIView,
    AdvertDetailsAPIView,
    PublicAdvertListAPIView
)

urlpatterns = [
    path('admin/plans/', PlanListAPIView.as_view()),
    path('publish/', PublicAdvertListAPIView.as_view()),
    path('admin/all-adverts/', AllAdvertsAPIView.as_view()),
    path('admin/adverts/<uuid:pk>/', AdvertDetailsAPIView.as_view()),
    path('admin/plans/details/<uuid:pk>/', PlanDetailsAPIView.as_view()),
]
