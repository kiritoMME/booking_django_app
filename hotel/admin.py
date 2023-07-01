from django.contrib import admin
from .models import Booking, Hotel, Room, Region

# Register your models here.
admin.site.register(Region)
admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Booking)