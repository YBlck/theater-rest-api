from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theater.models import Actor
from theater.serializers import ActorSerializer

ACTOR_URL = reverse("theater:actor-list")


class ActorAPITests(TestCase):
    """Setup DB for tests"""
    @classmethod
    def setUpTestData(cls):
        cls.test_user = get_user_model().objects.create_user(
            email="user@test.com", password="1qazcde3"
        )
        cls.test_admin = get_user_model().objects.create_user(
            email="admin@test.com", password="1qazcde3", is_staff=True
        )
        for i in range(5):
            Actor.objects.create(
                first_name=f"first_{i}",
                last_name=f"last_{i}",
            )


class AuthorizedUserTests(ActorAPITests):
    """Test API with regular user authentication"""
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_user)

    def test_actor_list(self):
        """Test that actor list works and return correct response"""
        response = self.client.get(ACTOR_URL)
        actors = Actor.objects.all()
        serializer = ActorSerializer(actors, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_actor_detail_does_not_exist(self):
        """Test that detail for actor does not exist"""
        actor = Actor.objects.first()
        url = f"{ACTOR_URL}/{actor.id}/"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_actor_create_forbidden(self):
        """Test that regular user can't create new actor"""
        payload = {
            "first_name": "first",
            "last_name": "last",
        }
        response = self.client.post(ACTOR_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserTests(ActorAPITests):
    """Test API with admin user authentication"""
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.test_admin)

    def test_actor_create_allowed(self):
        """Test that admin user can create new actor"""
        payload = {
            "first_name": "first",
            "last_name": "last",
        }
        response = self.client.post(ACTOR_URL, payload)
        actor = Actor.objects.get(id=response.data["id"])

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        for key in payload:
            self.assertEqual(payload[key], getattr(actor, key))
