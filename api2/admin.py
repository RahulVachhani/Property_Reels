from django.contrib import admin
from .models import Reel, User, Interaction, Location, Area

admin.site.register(Location)
@admin.register(Reel)
class ReelsAdmin(admin.ModelAdmin):
    search_fields = ['id',"location__location_name", 'area__area_name', 'property_type', 'price']
    # autocomplete_fields = ["location", "area"] 
    list_filter = ["property_type", "location", "area"]
    list_display = [
        "id", "location", 'area',"property_type"
    ]
    list_editable = ["property_type"]
# admin.site.register(Reel)
admin.site.register(User)
# admin.site.register(Interaction)
admin.site.register(Area)

@admin.register(Interaction)
class InsAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = [
        "id", "user", "reel"
    ]