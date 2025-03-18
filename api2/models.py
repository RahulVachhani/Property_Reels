from django.db import models


class Location(models.Model):
    location_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.location_name}'
    

class Area(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    area_name = models.CharField(max_length=1000)

    def __str__(self):
        return f'{self.location}  ==> {self.area_name}'


class User(models.Model):
    PROPERTY_TYPES = [
        ('villa', 'Villa'),
        ('flat', 'Flat'),
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('studio', 'Studio'),
        ('office', 'Office'),
    ]
    username = models.CharField(max_length=100)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    preferred_property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    min_price_preference = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_price_preference = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f'{self.username}'

class Reel(models.Model):
    PROPERTY_TYPES = [
        ('villa', 'Villa'),
        ('flat', 'Flat'),
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('studio', 'Studio'),
        ('office', 'Office'),
    ]

    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE)
    tags = models.TextField()
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)  
    shares = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.property_type} ==>  {self.area}'

class Interaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reel = models.ForeignKey(Reel, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False)
    watched_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.user}   {self.reel}'
    

    
