from django.urls import path, include
from rest_framework.routers import DefaultRouter

from theater.views import ActorViewSet, GenreViewSet, PlayViewSet, PerformanceViewSet

app_name = "theater"

router = DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("plays", PlayViewSet)
router.register("performances", PerformanceViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
