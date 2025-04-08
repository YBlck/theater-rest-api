from django.urls import path, include
from rest_framework.routers import DefaultRouter

from theater.views import (
    ActorViewSet,
    GenreViewSet,
    PlayViewSet,
    PerformanceViewSet,
    TheaterHallViewSet,
    ReservationViewSet,
)

app_name = "theater"

router = DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("theater-halls", TheaterHallViewSet, basename="theater-hall")
router.register("plays", PlayViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
