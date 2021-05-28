from rest_framework import serializers

from core.models import Recepie, Tag, Ingredient


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tag objects"""

    class Meta:
        model = Tag
        fields = ("id", "name")
        read_only_fields = ("id",)


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for Ingredient Objects"""

    class Meta:
        model = Ingredient
        fields = ("id", "name")
        read_only_fields = ("id",)


class RecepieSerializer(serializers.ModelSerializer):
    """Serializer for Recepie Objects"""
    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )

    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recepie
        fields = (
            "id",
            "title",
            "ingredients",
            "tags",
            "prep_time",
            "price",
            "link"
        )
        read_only_fields = ("id",)


class RecepieDetailSerializer(RecepieSerializer):
    """Serialize a Recepie Detail"""
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecepieImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recepies"""
    class Meta:
        model = Recepie
        fields = ('id', 'image')
        read_only_fields = ('id',)
