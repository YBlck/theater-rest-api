from rest_framework import serializers

from theater.models import Actor, Genre, Play, Performance


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name", "full_name")


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "image","actors", "genres")


class PlayListSerializer(PlaySerializer):
    actors = serializers.SlugRelatedField(many=True, read_only=True, slug_field="full_name")
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
    theater_hall_capacity = serializers.IntegerField(source="theater_hall.capacity", read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "play", "theater_hall", "show_time", "theater_hall_capacity")


