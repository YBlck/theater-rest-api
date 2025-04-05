from django.urls import path, include
from rest_framework.routers import DefaultRouter

from theater.views import ActorViewSet, GenreViewSet, PlayViewSet

app_name = "theater"

router = DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("plays", PlayViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
