from datetime import datetime, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theater.models import Performance, Play, TheaterHall, Reservation, Ticket
from theater.serializers import (
    ReservationListSerializer,
    ReservationSerializer,
)

RESERVATION_URL = reverse("theater:reservation-list")


class ReservationAPITests(TestCase):
    """Setup DB for tests"""
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
        cls.reservation_1 = Reservation.objects.create(user=cls.test_user)
        cls.reservation_2 = Reservation.objects.create(user=cls.test_user)
        cls.reservation_3 = Reservation.objects.create(user=cls.test_admin)
        cls.ticket_1 = Ticket.objects.create(
            row=1, seat=1, performance=cls.performance_1, reservation=cls.reservation_1
        )
        cls.ticket_2 = Ticket.objects.create(
            row=2, seat=2, performance=cls.performance_2, reservation=cls.reservation_2
        )
        cls.ticket_3 = Ticket.objects.create(
            row=3, seat=3, performance=cls.performance_3, reservation=cls.reservation_3
        )


class AuthorizedUserTests(ReservationAPITests):
    """Test API with regular user authentication"""
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_reservation_list(self):
        """Test that reservation list works and return correct response"""
        response = self.client.get(RESERVATION_URL)
        reservations = Reservation.objects.filter(user=self.test_user)
        serializer = ReservationListSerializer(reservations, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)
        self.assertIn("next", response.data)

    def test_reservation_create_with_tickets_allowed(self):
        """Test that reservation creates with tickets and return correct response"""
        payload = {
            "tickets": [
                {"row": 5, "seat": 5, "performance": self.performance_1.id},
                {"row": 6, "seat": 6, "performance": self.performance_1.id},
            ]
        }
        response = self.client.post(RESERVATION_URL, payload, format="json")
        reservation = Reservation.objects.get(id=response.data["id"])
        serializer = ReservationSerializer(reservation)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)

    def test_reservation_create_tickets_required(self):
        """Test that reservation required tickets for creation"""
        payload = {"tickets": []}
        response = self.client.post(RESERVATION_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reservation_taken_place_forbidden(self):
        """Test that reservation will be not created with when place is already taken"""
        payload = {
            "tickets": [{"row": 1, "seat": 1, "performance": self.performance_1.id}]
        }
        response = self.client.post(RESERVATION_URL, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
