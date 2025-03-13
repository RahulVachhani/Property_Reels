from django.db import models


class PropertyReel(models.Model):
    video = models.FileField(upload_to='property_reels/')  
    description = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.description[:50] 