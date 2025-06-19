from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.views import APIView

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Genre, Book, Comment
from .serializers import GenreSerializer, BookSerializer, RegisterSerializer, BookFilterSerializer, CommentSerializer

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.contrib.auth.models import User

from .permissions import IsOwnerOrReadOnly


@api_view(['GET'])
@permission_classes([AllowAny])
def get_csrf_token(request):
    try:
        token = get_token(request)
        return Response({'csrf_token': token})
    except Exception as e:
        return Response(
            {'detail': 'Ошибка сервера при получении CSRF токена', 'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# -----------------USER
class RegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=204)
        except Exception as e:
            return Response(status=400)


# ---------------------Books
# правила сваггера
@swagger_auto_schema(
    method='get',
    operation_summary="Список всех книг",
    operation_description="Возвращает список всех книг в базе данных.",
    responses={200: BookSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_books(request):
    queryset = Book.objects.all()
    serializer = BookSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


example_book = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['title', 'author', 'genre'],
    properties={
        'title': openapi.Schema(type=openapi.TYPE_STRING, example="Властелин колец"),
        'description': openapi.Schema(type=openapi.TYPE_STRING, example="Фэнтези-роман."),
        'author': openapi.Schema(type=openapi.TYPE_STRING, example="Дж. Р. Р. Толкин"),
        'genre': openapi.Schema(type=openapi.TYPE_ARRAY,
                                items=openapi.Items(type=openapi.TYPE_INTEGER),
                                example=[1, 2])
    }
)


@swagger_auto_schema(
    method='post',
    operation_summary="Добавить новую книгу",
    operation_description="Создает новую книгу. Требуется токен авторизации (Token <токен>).",
    request_body=example_book,
    responses={
        201: BookSerializer,
        400: 'Ошибка валидации данных'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_book(request):
    serializer = BookSerializer(data=request.data)
    if serializer.is_valid():
        book = serializer.save()

        # Уведомляем WebSocket-клиентов
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "books",
            {
                "type": "book.updated",
                "action": "add",
                "book_id": book.id,
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='patch',
    operation_summary="Частичное обновление книги",
    operation_description="Обновляет часть данных книги по ID. Требуется токен авторизации.",
    request_body=example_book,
    responses={200: BookSerializer, 400: 'Ошибка валидации'}
)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def patch_book(request, id):
    old_book = Book.objects.get(id=id)
    serializer = BookSerializer(old_book, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    operation_summary="Полное обновление книги",
    operation_description="Полностью обновляет книгу по ID. Требуется токен авторизации.",
    request_body=example_book,
    responses={200: BookSerializer, 400: 'Ошибка валидации'}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def put_book(request, id):
    old_book = Book.objects.get(id=id)
    serializer = BookSerializer(old_book, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    operation_summary="Удаление книги",
    operation_description="Удаляет книгу по ID. Только для администратора. Требуется токен авторизации.",
    responses={204: 'Книга удалена', 403: 'Нет прав', 404: 'Не найдено'}
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_book(request, id):
    book = Book.objects.get(id=id)
    book.delete()
    # Отправляем сообщение всем по WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "books",
        {
            "type": "book.updated",
            "action": "delete",
            "book_id": id,
        }
    )

    return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------------------------GENRES
@swagger_auto_schema(
    method='get',
    operation_summary="Список жанров",
    operation_description="Возвращает все жанры книг.",
    responses={200: GenreSerializer(many=True)}
)
@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_all_genres(request):
    queryset = Genre.objects.all()
    serializer = GenreSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([])
def get_genre_name(request, id):
    genre = Genre.objects.get(id=id)
    serializer = GenreSerializer(genre)
    return Response(serializer.data, status=status.HTTP_200_OK)


example_genre = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    required=['name'],
    properties={
        'name': openapi.Schema(type=openapi.TYPE_STRING, example="Фэнтези")
    }
)


@swagger_auto_schema(
    method='post',
    operation_summary="Добавить жанр",
    operation_description="Добавляет новый жанр. Требуется токен авторизации.",
    request_body=example_genre,
    responses={201: GenreSerializer, 400: 'Ошибка валидации'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_genre(request):
    serializer = GenreSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='put',
    operation_summary="Обновление жанра",
    operation_description="Полностью обновляет жанр по ID. Требуется токен авторизации.",
    request_body=example_genre,
    responses={200: GenreSerializer, 400: 'Ошибка валидации'}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def put_genre(request, id):
    old_genre = Genre.objects.get(id=id)
    serializer = GenreSerializer(old_genre, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    operation_summary="Удаление жанра",
    operation_description="Удаляет жанр по ID. Только для администратора. Требуется токен авторизации.",
    responses={204: 'Удалено', 403: 'Нет прав', 404: 'Не найдено'}
)
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_genre(request, id):
    genre = Genre.objects.get(id=id)
    genre.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# -------------------SORT
class BookListView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['genre']
    search_fields = ['title', 'author', 'description']
    ordering = ['id', 'title']

    @swagger_auto_schema(
        operation_summary="Фильтрация книг",
        operation_description="Позволяет фильтровать книги по автору и жанру.\n\nПример запроса:\n`/api/books/filter/?author=Толстой&genre=2`",
        manual_parameters=[
            openapi.Parameter('author', openapi.IN_QUERY, description="Имя автора", type=openapi.TYPE_STRING),
            openapi.Parameter('genre', openapi.IN_QUERY, description="ID жанра", type=openapi.TYPE_INTEGER)
        ],
        responses={200: BookSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    # ----------------------КОМЕНТАРИИ ДЛЯ ПРОВЕРКИ КАСТОМНОГО РАЗРЕЩЕНИЯ


class CommentCreateView(CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentListView(ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]


class CommentDeleteView(DestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]