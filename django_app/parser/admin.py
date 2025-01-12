from django.contrib import admin

from .models import OLXAd


@admin.register(OLXAd)
class OLXAdAdmin(admin.ModelAdmin):
    list_display = ["id_advertisement", "title", "date_published"]

