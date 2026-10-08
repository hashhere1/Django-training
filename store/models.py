from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from decimal import Decimal

"""
There are 3 types of models
-Concrete or standard model
-Abstract Model
-Proxy model
"""

#This is an abstract model. It works as a wrapper. It does not physically create a model in database. It just add the common fields in other data models.
#For example: created_at and updated_at fields are used in almost every table so we made an abstract table of these and we will inherit these properties into other tables.
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True     # This stops django from creating a model in database


#Standard or concrete model. Makes a physical model in the database.
class Product(TimeStampedModel):
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.1'))]) #Built in validator
    stock = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

    def clean(self):
        super().clean()
        if self.is_active and self.stock <=0:
            raise ValidationError({
                'stock': 'An active product must have ateast 1 item in stock otherwise disable is_active'
            })


#Proxy model is used to change the existing behavior of a model
class PremiumProduct(Product):
    class Meta:
        proxy = True
        ordering = ['-price'] #Changes the default sorting

    def is_expensive(self):
        return self.price > 1000
