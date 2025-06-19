from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Genre, Comment

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "description", "author", "genre"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user

# Сериализация запросов
class BookFilterSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False, min_value=1, default=1)
    search = serializers.CharField(required=False, allow_blank=True)
    genre = serializers.IntegerField(required=False, min_value=1)


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = ['id', 'author', 'book', 'text', 'created_at']