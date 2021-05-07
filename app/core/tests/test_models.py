from django.test import TestCase

from django.contrib.auth import get_user_model
from .. import models


def sample_user(email="testsample@test.com", password="testpass@123"):
    """Create a sample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test Creating a new user with an email is successful"""
        email = "test@test.com"
        password = "test@12345"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test User email is normalized"""
        email = "test@tESt.com"
        password = "test@12345"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, "123")

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            "test@test.com",
            "123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string repr"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name="Vegan",
        )
        self.assertEqual(str(tag), tag.name)
