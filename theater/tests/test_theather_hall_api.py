from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theater.models import TheaterHall
from theater.serializers import TheaterHallSerializer

THEATER_HALL_URL = reverse("theater:theater-hall-list")


class TheaterHallAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = get_user_model().objects.create_user(
            email="user@test.com", password="1qazcde3"
        )
        cls.test_admin = get_user_model().objects.create_user(
            email="admin@test.com", password="1qazcde3", is_staff=True
        )
        for i in range(5):
            TheaterHall.objects.create(
                name=f"hall_{i}",
                rows=10,
                seats_in_row=10,
            )


class AuthorizedUserTests(TheaterHallAPITests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_theater_hall_list(self):
        response = self.client.get(THEATER_HALL_URL)
        theater_halls = TheaterHall.objects.all()
        serializer = TheaterHallSerializer(theater_halls, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_theater_hall_detail_does_not_exist(self):
        theater_hall = TheaterHall.objects.first()
        url = f"{THEATER_HALL_URL}/{theater_hall.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_theater_hall_create_forbiden(self):
        payload = {
            "name": "test_hall",
            "rows": 10,
            "seats_in_row": 10,
        }
        response = self.client.post(THEATER_HALL_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTests(TheaterHallAPITests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_admin)

    def test_theater_hall_create_allowed(self):
        payload = {
            "name": "test_hall",
            "rows": 10,
            "seats_in_row": 10,
        }
        response = self.client.post(THEATER_HALL_URL, payload)
        hall = TheaterHall.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["capacity"], hall.capacity)
        for key in payload:
            self.assertEqual(payload[key], getattr(hall, key))
