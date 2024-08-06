from django.db import models
from django.utils.timezone import now
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class CarMake(models.Model):
    """
    Represents a car make.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()
    # Add any other fields as needed

    def __str__(self):
        return self.name  # Return the name as the string representation

class CarModel(models.Model):
    """
    Represents a car model, linked to a car make.
    """
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)  # Many-to-One relationship
    name = models.CharField(max_length=100)
    CAR_TYPES = [
        ('SEDAN', 'Sedan'),
        ('SUV', 'SUV'),
        ('WAGON', 'Wagon'),
        # Add more choices as required
    ]
    type = models.CharField(max_length=10, choices=CAR_TYPES, default='SUV')
    year = models.IntegerField(default=2023,
        validators=[
            MaxValueValidator(2023),
            MinValueValidator(2015)
        ])
    # Add any other fields as needed

    def __str__(self):
        return f'{self.name} ({self.car_make.name})'  # Return the name and car make as the string representation

    class Meta:
        ordering = ['name']  # Example: order by name

