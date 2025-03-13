from django.db import models


class Location(models.Model):
    location_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.location_name}'
    

class Area(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)
    area_name = models.CharField(max_length=2000, unique=True)

    def __str__(self):
        return f'{self.area_name}'


class Reels(models.Model):
    video = models.FileField(upload_to='reels/', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    area = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True)
    BHK_CHOICES = [
        ("flat", "FLAT"),
        ("villa", "VILLA"),
        ("house", "HOUSE"),
        ("studio", "STUDIO"),
        ("farm", "FARM"),
        ("penthouse", "Penthouse"),
        ("apartment", "Apartment"),
    ]

    property_type = models.CharField(
        max_length=20,
        choices=BHK_CHOICES,
        default="flat"
    )

    description = models.TextField()

    def __str__(self):
        return f'{self.location} ==> {self.description}'
    
