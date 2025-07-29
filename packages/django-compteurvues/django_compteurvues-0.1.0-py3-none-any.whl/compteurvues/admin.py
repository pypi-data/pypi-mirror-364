from django.contrib import admin
from .models import CompteurVue

@admin.register(CompteurVue)
class CompteurVueAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'object_id', 'total_vues')
    readonly_fields = ('content_type', 'object_id')
