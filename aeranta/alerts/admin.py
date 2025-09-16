from django.contrib import admin
from django.utils.html import format_html

from .models import Alert, Checker


@admin.register(Checker)
class CheckerAdmin(admin.ModelAdmin):
    list_display = ('parameter_name', 'api')
    search_fields = ('parameter_name', 'api')


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'image_tag', 'is_published')
    search_fields = ('name', 'slug')
    filter_horizontal = ('checkers', 'users')
    list_editable = ['is_published']


    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:100px; height:auto; object-fit:cover;" />', obj.image.url)
        return '-'
    image_tag.short_description = 'Image'
