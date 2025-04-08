from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient


ACTOR_URL = reverse("theater:actor-list")
GENRE_URL = reverse("theater:genre-list")
PLAY_URL = reverse("theater:play-list")
THEATER_HALL_URL = reverse("theater:theater-hall-list")
PERFORMANCE_URL = reverse("theater:performance-list")
RESERVATION_URL = reverse("theater:reservation-list")


class UnauthorizedUserTests(TestCase):
    """Test all theater endpoints without authentication"""
    def setUp(self):
        self.client = APIClient()

    def test_actor_endpoint_authorization_required(self):
        response = self.client.get(ACTOR_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_genre_endpoint_authorization_required(self):
        response = self.client.get(GENRE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_play_endpoint_authorization_required(self):
        response = self.client.get(PLAY_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_theater_hall_endpoint_authorization_required(self):
        response = self.client.get(THEATER_HALL_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_performance_endpoint_authorization_required(self):
        response = self.client.get(PERFORMANCE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reservation_endpoint_authorization_required(self):
        response = self.client.get(RESERVATION_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
