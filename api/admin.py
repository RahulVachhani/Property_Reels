from django.contrib import admin
from .models import Reels, Location, Area
from django import forms





@admin.register(Reels)
class ReelsAdmin1(admin.ModelAdmin):
    search_fields = ['id',"location__location_name",'area__area_name']
    autocomplete_fields = ["location", "area"] 
    list_filter = ["property_type", "location", "area"]
    list_display = [
        "id", "location", "area", "property_type"
    ]
    list_editable = ["property_type"]
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    search_fields = ["location_name"]

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    search_fields = ["area_name"]
    list_filter = ["location"] 





# class ReelsAdminForm(forms.ModelForm):
#     class Meta:
#         model = Reels
#         fields = "__all__"

#     def __init__(self, *args, **kwargs):
#         super(ReelsAdminForm, self).__init__(*args, **kwargs)
        
#         # If a location is already selected, filter areas accordingly
#         if "location" in self.data:
#             try:
#                 location_id = int(self.data.get("location"))
#                 self.fields["area"].queryset = Area.objects.filter(location_id=location_id)
#             except (ValueError, TypeError):
#                 self.fields["area"].queryset = Area.objects.none()
#         elif self.instance.pk:
#             self.fields["area"].queryset = self.instance.location.area_set.all()

# class ReelsAdmin(admin.ModelAdmin):
#     form = ReelsAdminForm

# admin.site.register(Reels, ReelsAdmin)