from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recepie

from .serializers import RecepieSerializer

RECEPIES_URL = reverse("recepie:recepie-list")


def sample_recepie(user, **params) -> Recepie:
    """Create and return a sample recepie"""
    recepie_params = {
        "title": "Sample recepie",
        "prep_time": 10,
        "price": 5.00,
    }
    recepie_params.update(params)

    return Recepie.objects.create(user=user, **recepie_params)


class PublicRecepieApiTests(TestCase):
    """Test unauthenticated recepie API access"""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required"""
        res = self.client.get(RECEPIES_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecepieApiTests(TestCase):
    """Test authenticated recepie API access"""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "testrecepie@test.com",
            "testpass@123",
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recepies(self):
        """Test retrieving a list of recepies"""
        sample_recepie(user=self.user)
        sample_recepie(user=self.user)

        res = self.client.get(RECEPIES_URL)

        recepies = Recepie.objects.all().order_by("id")
        serializer = RecepieSerializer(recepies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(len(serializer.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_recepies_limited_to_user(self):
        """Test retrieving recepies for user"""
        user2 = get_user_model().objects.create_user(
            "testrecepieother@test.com",
            "testpass@123",
        )
        sample_recepie(user=user2)
        sample_recepie(user=self.user)

        res = self.client.get(RECEPIES_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recepies = Recepie.objects.filter(user=self.user)
        serializer = RecepieSerializer(recepies, many=True)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
