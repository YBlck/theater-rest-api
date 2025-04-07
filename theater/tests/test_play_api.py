from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theater.models import Play, Genre, Actor
from theater.serializers import PlayListSerializer, PlayDetailSerializer

PLAY_URL = reverse("theater:play-list")


class PlayAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = get_user_model().objects.create_user(
            email="user@test.com", password="1qazcde3"
        )
        cls.test_admin = get_user_model().objects.create_user(
            email="admin@test.com", password="1qazcde3", is_staff=True
        )
        cls.genre_1 = Genre.objects.create(name="test_genre_1")
        cls.genre_2 = Genre.objects.create(name="test_genre_2")
        cls.genre_3 = Genre.objects.create(name="test_genre_3")
        cls.actor_1 = Actor.objects.create(first_name="first_1", last_name="last_1")
        cls.actor_2 = Actor.objects.create(first_name="first_2", last_name="last_2")
        cls.actor_3 = Actor.objects.create(first_name="first_3", last_name="last_3")
        cls.play_1 = Play.objects.create(title="test_play_1")
        cls.play_2 = Play.objects.create(title="test_play_2")
        cls.play_3 = Play.objects.create(title="test_play_3")

        cls.play_1.genres.add(cls.genre_1.id)
        cls.play_1.actors.add(cls.actor_1.id)


class AuthorizedUserTests(PlayAPITests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_play_list(self):
        response = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlayListSerializer(plays, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_play_list_filter_by_title(self):
        response = self.client.get(PLAY_URL, {"title": self.play_1.title})

        serializer_play_1 = PlayListSerializer(self.play_1)
        serializer_play_2 = PlayListSerializer(self.play_2)
        serializer_play_3 = PlayListSerializer(self.play_3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_play_1.data, response.data)
        self.assertNotIn(serializer_play_2.data, response.data)
        self.assertNotIn(serializer_play_3.data, response.data)
        self.assertEqual(len(response.data), 1)

    def test_play_list_filter_by_genres(self):
        response = self.client.get(PLAY_URL, {"genres": self.genre_1.id})

        serializer_play_1 = PlayListSerializer(self.play_1)
        serializer_play_2 = PlayListSerializer(self.play_2)
        serializer_play_3 = PlayListSerializer(self.play_3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_play_1.data, response.data)
        self.assertNotIn(serializer_play_2.data, response.data)
        self.assertNotIn(serializer_play_3.data, response.data)
        self.assertEqual(len(response.data), 1)

    def test_play_list_filter_by_actors(self):
        response = self.client.get(PLAY_URL, {"actors": self.actor_1.id})

        serializer_play_1 = PlayListSerializer(self.play_1)
        serializer_play_2 = PlayListSerializer(self.play_2)
        serializer_play_3 = PlayListSerializer(self.play_3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_play_1.data, response.data)
        self.assertNotIn(serializer_play_2.data, response.data)
        self.assertNotIn(serializer_play_3.data, response.data)
        self.assertEqual(len(response.data), 1)

    def test_play_detail(self):
        url = reverse("theater:play-detail", args=[self.play_1.id])
        response = self.client.get(url)
        serializer = PlayDetailSerializer(self.play_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_play_create_forbidden(self):
        payload = {
            "title": "test_play",
        }
        response = self.client.post(PLAY_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTests(PlayAPITests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_admin)

    def test_play_create_allowed(self):
        payload = {
            "title": "test_title",
            "description": "test_description",
        }
        response = self.client.post(PLAY_URL, payload)
        play = Play.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(play, key))

    def test_create_movie_with_genres_and_actors(self):
        payload = {
            "title": "test",
            "description": "test",
            "genres": [self.genre_1.id, self.genre_2.id],
            "actors": [self.actor_1.id, self.actor_2.id],
        }
        response = self.client.post(PLAY_URL, payload)
        movie = Play.objects.get(id=response.data["id"])
        genres = movie.genres.all()
        actors = movie.actors.all()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(self.genre_1, genres)
        self.assertIn(self.genre_2, genres)
        self.assertNotIn(self.genre_3, genres)
        self.assertIn(self.actor_1, actors)
        self.assertIn(self.actor_2, actors)
        self.assertNotIn(self.actor_3, actors)
        self.assertEqual(len(genres), 2)
        self.assertEqual(len(actors), 2)

    def test_play_delete_not_allowed(self):
        play = Play.objects.create(
            title="test_title",
            description="test_description",
        )
        url = reverse("theater:play-detail", args=[play.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
