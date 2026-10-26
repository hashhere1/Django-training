from django.contrib import admin
from .models import Book, Author, Publisher, TechBook, Member, Borrow


admin.site.register(Author)
admin.site.register(Borrow)
admin.site.register(Book)
admin.site.register(Publisher)
admin.site.register(TechBook)
admin.site.register(Member)
