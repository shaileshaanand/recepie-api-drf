from unittest.mock import patch

from django.test import TestCase

from django.contrib.auth import get_user_model
from .. import models


def sample_user(email="testsample@test.com",
                password="testpass@123") -> models.User:
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

    def test_ingredient_str(self):
        """Test the ingredient string repr"""
        ingredient = models.Ingredient.objects.create(
            user=sample_user(),
            name="Potato",
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recepie_str(self):
        """Test the recepie string repr"""
        recepie = models.Recepie.objects.create(
            user=sample_user(),
            title="Tomato Soup",
            price=5.0,
            prep_time=5,
        )
        self.assertEqual(str(recepie), recepie.title)

    @patch("uuid.uuid4")
    def test_recepie_file_name_uuid(self, mock_uuid):
        """Test that image is saveed in the correct location"""
        uuid = "test-uuid"
        mock_uuid.return_value = uuid
        file_path = models.recepie_image_file_path(None, "myimage.jpg")
        exp_path = f"uploads/recepie/{uuid}.jpg"
        self.assertEqual(file_path, exp_path)
