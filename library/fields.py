from django.core.validators import RegexValidator
from django.db import models


class ISBNField(models.CharField):
    default_validators = [RegexValidator(r"^\d{13}$", "ISBN should consist of 13 digits")]

    def __init__(self, *args, **kwargs):
        kwargs["max_length"] = 13
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def to_python(self, value):
        value = super().to_python(value)
        if value:
            value = value.replace("-", "").replace(" ", "")
        return value

    def formfield(self, **kwargs):
        kwargs["max_length"] = 17
        return super().formfield(**kwargs)