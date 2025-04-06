from datetime import datetime

from django.db.models import F
from django.db.models.aggregates import Count
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from theater.models import Actor, Genre, Play, Performance, TheaterHall, Reservation
from theater.serializers import (
    ActorSerializer,
    GenreSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    PlayImageSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    TheaterHallSerializer,
    PerformanceDetailSerializer,
    ReservationSerializer,
    ReservationListSerializer,
    ActorImageSerializer,
)


class ActorViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer

    def get_serializer_class(self):
        if self.action == "upload_image":
            return ActorImageSerializer
        return ActorSerializer

    @action(
        detail=True,
        methods=["POST"],
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading an image for an actor."""
        actor = self.get_object()
        serializer = self.get_serializer(actor, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TheaterHallViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = TheaterHall.objects.all()
    serializer_class = TheaterHallSerializer


class PlayViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer

    @staticmethod
    def _params_to_ints(params) -> list[int]:
        """Convert a list of string IDs to a list of integers"""
        return [int(param_id) for param_id in params.split(",")]

    def get_queryset(self):
        """Plays filtering by title, actor or genre"""
        title = self.request.query_params.get("title")
        actors = self.request.query_params.get("actors")
        genres = self.request.query_params.get("genres")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if actors:
            actors_ids = self._params_to_ints(actors)
            queryset = queryset.filter(actors__in=actors_ids)

        if genres:
            genres_ids = self._params_to_ints(genres)
            queryset = queryset.filter(genres__in=genres_ids)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        if self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                description="Filter by title",
                type=OpenApiTypes.STR,
                required=False,
            ),
            OpenApiParameter(
                name="genres",
                description="Filter by genres",
                type={"type": "array", "items": {"type": "integer"}},
                required=False,
            ),
            OpenApiParameter(
                name="actors",
                description="Filter by actors",
                type={"type": "array", "items": {"type": "integer"}},
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of plays"""
        return super().list(request, *args, **kwargs)

    @action(
        detail=True,
        methods=["POST"],
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading an image to a play"""
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.select_related("play", "theater_hall").annotate(
        tickets_available=(
            F("theater_hall__rows") * F("theater_hall__seats_in_row") - Count("tickets")
        )
    )
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        """Performance filtering by play and date"""
        play_id = self.request.query_params.get("play")
        date = self.request.query_params.get("date")

        queryset = self.queryset

        if play_id:
            queryset = queryset.filter(play=int(play_id))

        if date:
            date = datetime.strptime(date, "%Y-%m-%d")
            queryset = queryset.filter(show_time__date=date)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return PerformanceSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                description="Filter by date",
                type=OpenApiTypes.DATE,
                required=False,
            ),
            OpenApiParameter(
                name="play",
                description="Filter by play",
                type={"type": "array", "items": {"type": "integer"}},
                required=False,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of performances"""
        return super().list(request, *args, **kwargs)


class ReservationViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play",
        "tickets__performance__theater_hall",
    )
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ReservationListSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
