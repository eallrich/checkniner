from django.contrib import admin

from .models import AircraftType, Airstrip, Checkout

admin.site.register(AircraftType)
admin.site.register(Airstrip)
admin.site.register(Checkout)

