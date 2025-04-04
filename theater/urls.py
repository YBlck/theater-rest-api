from django.urls import path, include
from rest_framework.routers import DefaultRouter

from theater.views import ActorViewSet

app_name = "theater"

router = DefaultRouter()
router.register("actors", ActorViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
