from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recepie, Tag, Ingredient

from ..serializers import RecepieSerializer, RecepieDetailSerializer

RECEPIES_URL = reverse("recepie:recepie-list")


def detail_url(recepie_id) -> str:
    return reverse("recepie:recepie-detail", args=[recepie_id])


def sample_tag(user, name="Main Course") -> Tag:
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name="Cinnamon") -> Ingredient:
    return Ingredient.objects.create(user=user, name=name)


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

    def test_view_recepie_detail(self):
        """Test viewing a recepie detail"""
        recepie = sample_recepie(user=self.user)
        recepie.tags.add(sample_tag(user=self.user))
        recepie.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recepie.id)
        res = self.client.get(url)

        serializer = RecepieDetailSerializer(recepie)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recepie(self):
        """Test creating recepie"""
        payload = {
            "title": "Choclate soup",
            "prep_time": 30,
            "price": 5.0,
        }
        res = self.client.post(RECEPIES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recepie = Recepie.objects.get(id=res.data["id"])

        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recepie, key))

    def test_create_recepie_with_tags(self):
        """Test creating a recepie with tags"""
        tag1 = sample_tag(user=self.user, name="Vegan")
        tag2 = sample_tag(user=self.user, name="Dessert")
        payload = {
            "title": "Gulab Jamun",
            "tags": [tag1.id, tag2.id],
            "prep_time": 60,
            "price": 20.0
        }
        res = self.client.post(RECEPIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recepie = Recepie.objects.get(id=res.data["id"])
        tags = recepie.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recepie_with_ingredients(self):
        """Test creating recepie with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name="Vegan")
        ingredient2 = sample_ingredient(user=self.user, name="Dessert")
        payload = {
            "title": "Gulab Jamun",
            "ingredients": [ingredient1.id, ingredient2.id],
            "prep_time": 60,
            "price": 20.0
        }
        res = self.client.post(RECEPIES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recepie = Recepie.objects.get(id=res.data["id"])
        ingredients = recepie.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_update_recepie_update_partial(self):
        """Test updating a recepie with patch"""
        recepie = sample_recepie(user=self.user)
        recepie.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name="Curry")

        payload = {
            "title": "Chicken Tikka",
            "tags": [new_tag.id]
        }
        url = detail_url(recepie.id)
        self.client.patch(url, payload)

        recepie.refresh_from_db()
        self.assertEqual(recepie.title, payload["title"])
        tags = recepie.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_update_recepie_full(self):
        """Test updating a recepie with put"""
        recepie = sample_recepie(user=self.user)
        recepie.tags.add(sample_tag(user=self.user))
        payload = {
            "title": "Not Chicken Tikka",
            "prep_time": 25,
            "price": 5.0,
        }
        url = detail_url(recepie.id)
        self.client.put(url, payload)

        recepie.refresh_from_db()
        self.assertEqual(recepie.title, payload["title"])
        self.assertEqual(recepie.prep_time, payload["prep_time"])
        self.assertEqual(recepie.price, payload["price"])
