from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from theater.models import (
    Actor,
    Genre,
    Play,
    Performance,
    TheaterHall,
    Ticket,
    Reservation,
)


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name", "full_name", "image")


class ActorImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "image")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class TheaterHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheaterHall
        fields = ("id", "name", "rows", "seats_in_row", "capacity")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "image", "actors", "genres")


class PlayListSerializer(PlaySerializer):
    actors = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )
    genres = serializers.SlugRelatedField(many=True, read_only=True, slug_field="name")


class PlayDetailSerializer(PlaySerializer):
    actors = ActorSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)


class PlayImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "image")


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ("id", "play", "theater_hall", "show_time")


class PerformanceListSerializer(PerformanceSerializer):
    play = serializers.CharField(source="play.title", read_only=True)
    theater_hall = serializers.CharField(source="theater_hall.name", read_only=True)
    theater_hall_capacity = serializers.IntegerField(
        source="theater_hall.capacity", read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Performance
        fields = (
            "id",
            "play",
            "theater_hall",
            "show_time",
            "theater_hall_capacity",
            "tickets_available",
        )


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["performance"].theater_hall,
            ValidationError,
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class TicketListSerializer(TicketSerializer):
    performance = PerformanceListSerializer(many=False, read_only=True)


class TicketTakenSeatsSerializer(TicketSerializer):
    class Meta:
        model = Ticket
        fields = ("row", "seat")


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlayListSerializer(read_only=True, many=False)
    theater_hall = TheaterHallSerializer(read_only=True, many=False)
    taken_places = TicketTakenSeatsSerializer(
        many=True, read_only=True, source="tickets"
    )

    class Meta:
        model = Performance
        fields = ("id", "play", "theater_hall", "show_time", "taken_places")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(reservation=reservation, **ticket_data)
            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
