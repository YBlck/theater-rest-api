from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient

from theater.models import Genre
from theater.serializers import GenreSerializer

GENRE_URL = reverse("theater:genre-list")


class GenreAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = get_user_model().objects.create_user(
            email="user@test.com", password="1qazcde3"
        )
        cls.test_admin = get_user_model().objects.create_user(
            email="admin@test.com", password="1qazcde3", is_staff=True
        )
        for i in range(5):
            Genre.objects.create(name=f"genre_{i}")


class AuthorizedUserTests(GenreAPITests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_genre_list(self):
        response = self.client.get(GENRE_URL)
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_genre_detail_does_not_exist(self):
        genre = Genre.objects.first()
        url = f"{GENRE_URL}/{genre.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_genre_create_forbidden(self):
        payload = {"name": "test_genre"}
        response = self.client.post(GENRE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTests(GenreAPITests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_admin)

    def test_genre_create_allowed(self):
        payload = {"name": "test_genre"}
        response = self.client.post(GENRE_URL, payload)
        genre = Genre.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(genre, key))
