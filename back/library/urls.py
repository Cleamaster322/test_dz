from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import *
urlpatterns = [
    path('books/', get_all_books, name="books"),
    path('add_book/', post_book, name="add_book"),
    path('put_book/<int:id>/', put_book, name="put_book"),
    path('patch_book/<int:id>/', patch_book, name="patch_book"),
    path('delete_book/<int:id>/', delete_book, name="delete_book"),


    path('genres/', get_all_genres, name="genres"),
    path('genre/<int:id>/', get_genre_name, name="genre_name"),
    path('add_genre/', post_genre, name="add_genre"),
    path('put_genre/<int:id>/', put_genre, name="put_genre"),
    path('delete_genre/<int:id>/', delete_genre, name="delete_genre"),

    path('filter/', BookListView.as_view(), name="filter"),


    # Авторизация
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', TokenObtainPairView.as_view(), name="login"),
    path('refresh/', TokenRefreshView.as_view(), name="token_refresh"),
    path('logout/', LogoutView.as_view(), name="logout"),

    path('get_csrf_token/', get_csrf_token, name="get_csrf_token"),

    #Комментарии
    path('comments/', CommentListView.as_view(), name='comment-list'),
    path('comments/add/', CommentCreateView.as_view(), name='comment-add'),
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),
]