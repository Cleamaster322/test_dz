from django.contrib import admin
from .models import Genre, Book
# Register your models here.

# что бы бд отабражалось в админке
admin.site.register(Genre)
admin.site.register(Book)