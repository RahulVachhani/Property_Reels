from django.db import models


class Location(models.Model):
    location_name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return f'{self.location_name}'
    

class Reels(models.Model):
    video = models.FileField(upload_to='reels/', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.location} ==> {self.description}'
    
