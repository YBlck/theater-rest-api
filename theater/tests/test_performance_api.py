from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.db.models import F
from django.db.models.aggregates import Count
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theater.models import Performance, Play, TheaterHall
from theater.serializers import (
    PerformanceListSerializer,
    PerformanceDetailSerializer,
)

PERFORMANCE_URL = reverse("theater:performance-list")


def detail_url(obj_id):
    return reverse("theater:performance-detail", args=[obj_id])


class PerformanceAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user = get_user_model().objects.create_user(
            email="user@test.com", password="1qazcde3"
        )
        cls.test_admin = get_user_model().objects.create_user(
            email="admin@test.com", password="1qazcde3", is_staff=True
        )
        cls.play_1 = Play.objects.create(title="test_play_1")
        cls.play_2 = Play.objects.create(title="test_play_2")
        cls.play_3 = Play.objects.create(title="test_play_3")
        cls.hall_1 = TheaterHall.objects.create(
            name="test_hall_1", rows=10, seats_in_row=10
        )
        cls.hall_2 = TheaterHall.objects.create(
            name="test_hall_2", rows=10, seats_in_row=10
        )
        cls.hall_3 = TheaterHall.objects.create(
            name="test_hall_3", rows=10, seats_in_row=10
        )
        cls.performance_1 = Performance.objects.create(
            play=cls.play_1,
            theater_hall=cls.hall_1,
            show_time=datetime(2025, 10, 10, 18, 00, tzinfo=timezone.utc),
        )
        cls.performance_2 = Performance.objects.create(
            play=cls.play_2,
            theater_hall=cls.hall_2,
            show_time=datetime(2025, 10, 11, 18, 00, tzinfo=timezone.utc),
        )
        cls.performance_3 = Performance.objects.create(
            play=cls.play_3,
            theater_hall=cls.hall_3,
            show_time=datetime(2025, 10, 12, 18, 00, tzinfo=timezone.utc),
        )


class AuthorizedUserTests(PerformanceAPITests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_performance_list(self):
        response = self.client.get(PERFORMANCE_URL)
        performances = Performance.objects.all().annotate(
            tickets_available=(
                F("theater_hall__rows") * F("theater_hall__seats_in_row")
                - Count("tickets")
            )
        )
        serializer = PerformanceListSerializer(performances, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_performance_list_filter_by_play(self):
        response = self.client.get(PERFORMANCE_URL, data={"play": self.play_1.id})
        performances = Performance.objects.all().annotate(
            tickets_available=(
                F("theater_hall__rows") * F("theater_hall__seats_in_row")
                - Count("tickets")
            )
        )
        performance_1 = performances.get(play=self.play_1.id)
        performance_2 = performances.get(play=self.play_2.id)
        performance_3 = performances.get(play=self.play_3.id)

        serializer_1 = PerformanceListSerializer(performance_1)
        serializer_2 = PerformanceListSerializer(performance_2)
        serializer_3 = PerformanceListSerializer(performance_3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data)
        self.assertNotIn(serializer_2.data, response.data)
        self.assertNotIn(serializer_3.data, response.data)
        self.assertEqual(len(response.data), 1)

    def test_performance_list_filter_by_date(self):
        response = self.client.get(PERFORMANCE_URL, data={"date": "2025-10-10"})
        performances = Performance.objects.all().annotate(
            tickets_available=(
                F("theater_hall__rows") * F("theater_hall__seats_in_row")
                - Count("tickets")
            )
        )
        performance_1 = performances.get(play=self.play_1.id)
        performance_2 = performances.get(play=self.play_2.id)
        performance_3 = performances.get(play=self.play_3.id)

        serializer_1 = PerformanceListSerializer(performance_1)
        serializer_2 = PerformanceListSerializer(performance_2)
        serializer_3 = PerformanceListSerializer(performance_3)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, response.data)
        self.assertNotIn(serializer_2.data, response.data)
        self.assertNotIn(serializer_3.data, response.data)
        self.assertEqual(len(response.data), 1)

    def test_performance_detail(self):
        url = detail_url(self.performance_1.id)
        response = self.client.get(url)
        serializer = PerformanceDetailSerializer(self.performance_1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, response.data)

    def test_performance_create_forbidden(self):
        payload = {
            "play": self.play_1.id,
            "theater_hall": self.hall_1.id,
            "show_time": datetime(2025, 10, 13, 18, 00, tzinfo=timezone.utc),
        }
        response = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_performance_delete_forbidden(self):
        performance = Performance.objects.create(
            play=self.play_1,
            theater_hall=self.hall_1,
            show_time=datetime(2025, 10, 13, 18, 00, tzinfo=timezone.utc),
        )
        url = detail_url(performance.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTests(PerformanceAPITests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_admin)

    def test_performance_create_allowed(self):
        payload = {
            "play": self.play_1.id,
            "theater_hall": self.hall_1.id,
            "show_time": datetime(2025, 10, 13, 18, 00, tzinfo=timezone.utc),
        }
        response = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_performance_delete_allowed(self):
        performance = Performance.objects.create(
            play=self.play_1,
            theater_hall=self.hall_1,
            show_time=datetime(2025, 10, 13, 18, 00, tzinfo=timezone.utc),
        )
        url = detail_url(performance.id)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
