from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator
from datetime import date
from django.db.models import F, Q
from django.conf import settings


def validate_not_future_year(value):
    if value > date.today().year:
        raise ValidationError(
            f"{value} is future year. Not allowed."
        )

def validate_not_blank(value):
    if not value.strip():
        raise ValidationError("Title cannot be whitespace only")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Author(TimeStampedModel):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    born_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Author id= {self.id}, name= {self.name!r}"


class Publisher(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name
    

class Book(TimeStampedModel):
    class Genre(models.TextChoices):
        FICTION = "FIC", "Fiction"
        SCIENCE = "SCI", "Science"
        TECH = "TEC", "Technology"

    class Language(models.TextChoices):
        ENGLISH = "EN", "English"
        URDU = "UR", "Urdu"
        ARABIC = "AR", "Arabic"


    title = models.CharField(max_length=200, db_index=True, validators=[validate_not_blank], help_text="Book Title")
    isbn = models.CharField(max_length=13, unique=True, validators=[RegexValidator(r"^\d{13}$", "ISBN should be consists of 13 numbers")])
    genre = models.CharField(max_length=3, choices=Genre.choices, default=Genre.FICTION)
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)], )
    published_year = models.PositiveIntegerField(validators=[MinValueValidator(1450), validate_not_future_year])
    rating = models.FloatField(null=True, blank=True, validators=[MinValueValidator(0), MaxValueValidator(5)])
    language = models.CharField(max_length=2, choices=Language.choices, default=Language.ENGLISH)
    description = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True, related_name="books")
    authors = models.ManyToManyField(Author, related_name="books", blank=True)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = "Books"
        indexes = [models.Index(fields=["genre", "published_year"])]
        constraints = [models.CheckConstraint(condition=Q(price__gte=0), name="book_price_gte_0")]

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<Book id={self.id} isbn={self.isbn}>"

    @property
    def age(self):
        return date.today().year - self.published_year

    @staticmethod
    def is_valid_isbn_format(isbn):
        return isbn.isdigit() and len(isbn) == 13

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

class TechBook(Book):
    class Meta:
        proxy = True
        ordering = ["-published_year"]

    def short_info(self):
        return f"{self.title} ({self.published_year})"


class Member(TimeStampedModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="member")
    phone = models.CharField(max_length=15, blank=True)
    joined_on = models.DateField(default=date.today)

    def __str__(self):
        return self.user.username


class Borrow(TimeStampedModel):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="borrows")
    book = models.ForeignKey(Book, on_delete=models.PROTECT, related_name="borrows")
    borrowed_on = models.DateField(default=date.today)
    due_date = models.DateField()
    returned_on = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["-borrowed_on"]
        constraints = [
            models.CheckConstraint(condition=Q(due_date__gte=F("borrowed_on")), name="borrowed_due_after_borrowed")
        ]

    def __str__(self):
        return f"{self.member} -> {self.book}"

    @property
    def is_overdue(self):
        return self.returned_on is None and self.due_date < date.today()

