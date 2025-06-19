from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import Book, Genre


class AuthTestCase(APITestCase):
    def setUp(self):
        self.register_url = '/lb/register/'
        self.login_url = '/lb/login/'
        self.logout_url = '/lb/logout/'
        self.refresh_url = '/lb/refresh/'

        self.user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "strongpassword123"
        }

    def test_user_can_register(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_user_can_login(self):
        User.objects.create_user(
            username=self.user_data["username"],
            email=self.user_data["email"],
            password=self.user_data["password"]
        )
        response = self.client.post(self.login_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_can_logout(self):
        # Регистрация
        self.client.post(self.register_url, self.user_data, format='json')

        # Вход
        response = self.client.post(self.login_url, {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }, format='json')
        access = response.data["access"]
        refresh = response.data["refresh"]

        # Logout
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(self.logout_url, {"refresh": refresh}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_with_invalid_refresh_token(self):
        User.objects.create_user(username="user", password="testpass")
        response = self.client.post(self.login_url, {
            "username": "user",
            "password": "testpass"
        }, format='json')
        access = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(self.logout_url, {"refresh": "invalid_refresh"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_without_refresh_token_field(self):
        User.objects.create_user(username="user", password="testpass")
        response = self.client.post(self.login_url, {
            "username": "user",
            "password": "testpass"
        }, format='json')
        access = response.data["access"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        response = self.client.post(self.logout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class BookGenreAPITest(APITestCase):
    def setUp(self):
        # Создание пользователей
        self.user = User.objects.create_user(username="user", password="pass")
        self.admin = User.objects.create_superuser(username="admin", password="adminpass", email="admin@example.com")

        # Получение JWT токенов
        self.user_tokens = self._get_tokens_for_user("user", "pass")
        self.admin_tokens = self._get_tokens_for_user("admin", "adminpass")

        # Клиенты с авторизацией (JWT)
        self.auth_client = APIClient()
        self.auth_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.user_tokens['access'])

        self.admin_client = APIClient()
        self.admin_client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.admin_tokens['access'])

        # Тестовые жанр и книга
        self.genre = Genre.objects.create(name="Фантастика")
        self.book = Book.objects.create(title="Пример книги", author="Автор", description="описание")
        self.book.genre.set([self.genre])

    def _get_tokens_for_user(self, username, password):
        response = self.client.post(reverse('login'), {
            "username": username,
            "password": password
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        return {
            "access": response.data["access"],
            "refresh": response.data["refresh"]
        }
    
    # --- КНИГИ ---
    def test_get_all_books(self):
        url = reverse('books')  # путь должен соответствовать твоему urls.py
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_book_authenticated(self):
        url = reverse('add_book')
        data = {'title': 'Новая книга', 'author': 'Новый автор','description':'описание', 'genre': self.genre.id}
        response = self.auth_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_book_unauthenticated(self):
        url = reverse('add_book')
        data = {'title': 'Новая книга', 'author': 'Новый автор', 'description':'описание', 'genre': self.genre.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_book(self):
        url = reverse('patch_book', kwargs={'id': self.book.id})
        data = {'title': 'Обновлённая книга'}
        response = self.auth_client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(self.book.title, 'Обновлённая книга')

    def test_put_book(self):
        url = reverse('put_book', kwargs={'id': self.book.id})
        data = {'title': 'Полная замена', 'author': 'Новый автор', 'description':'описание', 'genre': self.genre.id}
        response = self.auth_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_book_as_admin(self):
        url = reverse('delete_book', kwargs={'id': self.book.id})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_book_as_user(self):
        url = reverse('delete_book', kwargs={'id': self.book.id})
        response = self.auth_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- ЖАНРЫ ---
    def test_get_all_genres(self):
        url = reverse('genres')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_genre(self):
        url = reverse('add_genre')
        data = {'name': 'Детектив'}
        response = self.auth_client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_put_genre(self):
        url = reverse('put_genre', kwargs={'id': self.genre.id})
        data = {'name': 'Хоррор'}
        response = self.auth_client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_genre_as_admin(self):
        url = reverse('delete_genre', kwargs={'id': self.genre.id})
        response = self.admin_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_genre_as_user(self):
        url = reverse('delete_genre', kwargs={'id': self.genre.id})
        response = self.auth_client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- СОРТИРОВКА ---
    def test_book_list_filter_by_author(self):
        url = reverse('filter') + f'?author={self.book.author}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)